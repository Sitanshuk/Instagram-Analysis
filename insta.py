from selenium import webdriver
from time import sleep
from bs4 import BeautifulSoup
import json
from urllib.request import urlretrieve
import pandas as pd
import os


class LoginPage:
    def __init__(self, browser):
        self.browser = browser

    def login(self, username, password):
        username_input = self.browser.find_element_by_css_selector("input[name='username']")
        password_input = self.browser.find_element_by_css_selector("input[name='password']")
        username_input.send_keys(username)
        password_input.send_keys(password)
        login_button = self.browser.find_element_by_xpath("//button[@type='submit']")
        login_button.click()
        if 'logged-in' in self.browser.page_source:
            print('Logged in')

class HomePage:
    def __init__(self, browser):
        self.browser = browser
        self.browser.get('https://www.instagram.com/')

    def go_to_login_page(self):
        # self.browser.find_element_by_xpath("//a[text()='Log In']").click()
        sleep(5)
        return LoginPage(self.browser)

class Profile:
    """docstring for Profile"""
    def __init__(self, browser):
        self.browser = browser
        sleep(2)
    def getProfile(self, username):
        self.browser.get(f'https://www.instagram.com/{username}/')
        sleep(5)
        self.browser.save_screenshot('profile.png')
        soup = BeautifulSoup(self.browser.page_source, 'html.parser')
        div = soup.find('div')
        bio = div.find_all('span')[0].text
        ul = soup.find('ul')
        li = ul.find_all('li')
        no_of_post, no_of_follower, no_of_following = [l.text for l in li]

        image_tiles = soup.find_all('img')
        image_captions = [tile['alt'] for tile in image_tiles]
        image_urls = [tile['src'] for tile in image_tiles]
        os.mkdir("Dataset/Train/" + username)
        os.mkdir("Dataset/Valid/" + username)
        for i in range(min(12, len(image_urls))):
            if i < 8:
                urlretrieve(image_urls[i], f"Dataset/Train/{username}/{username} pic {i}.png")
            else:
                urlretrieve(image_urls[i], f"Dataset/Valid/{username}/{username} pic {i}.png")
        return bio, no_of_post, no_of_follower, no_of_following, image_captions

    def getFollowing(self, save = False):
        self.browser.get('https://www.instagram.com/accounts/access_tool/accounts_you_follow')
        sleep(10)
        self.browser.save_screenshot('accounts_you_follow.png')
        try:
            while self.browser.find_element_by_xpath("//button[@type='button']"):
                self.browser.find_element_by_xpath("//button[@type='button']").click()
                sleep(2)
                self.browser.save_screenshot('accounts_you_follow.png')
        except:
            self.browser.save_screenshot('accounts_you_follow.png')
        soup = BeautifulSoup(self.browser.page_source, 'html.parser')
        following_soup = soup.find_all('div', attrs={'class': '-utLf'})
        my_following_list = list()
        for f in following_soup:
            my_following_list.append(f.text)
        if save:
            with open('following.txt', 'w') as f:
                for following in my_following_list:
                    f.write(following + '\n')
        return my_following_list

    def getFollower(self, save = False):
        self.browser.get('https://www.instagram.com/accounts/access_tool/accounts_following_you')
        sleep(10)
        self.browser.save_screenshot('accounts_following_you.png')
        try:
            while self.browser.find_element_by_xpath("//button[@type='button']"):
                self.browser.find_element_by_xpath("//button[@type='button']").click()
                sleep(2)
                self.browser.save_screenshot('accounts_following_you.png')
        except:
            self.browser.save_screenshot('accounts_following_you.png')
        soup = BeautifulSoup(self.browser.page_source, 'html.parser')
        follower_soup = soup.find_all('div', attrs={'class': '-utLf'})
        my_followers_list = list()
        for f in follower_soup:
            my_followers_list.append(f.text)
        if save:
            with open('following.txt', 'w') as f:
                for follower in my_followers_list:
                    f.write(follower + '\n')
        return my_followers_list


def getinsta(username, password):
    browser = webdriver.PhantomJS()
    browser.implicitly_wait(1)
    home_page = HomePage(browser)
    login_page = home_page.go_to_login_page()
    login_page.login(username, password)
    errors = browser.find_elements_by_css_selector('#error_message')
    assert len(errors) == 0
    return browser


class Dataset:
    def __init__(self, browser):
        self.browser = browser

    def genDataset(self, username):
        bio_list = list()
        no_of_post_list  = list()
        no_of_follower_list  = list()
        no_of_following_list  = list()
        image_captions_list  = list()
        myprofile = Profile(self.browser)
        my_following_list = myprofile.getFollowing(save = False)
        my_followers_list = myprofile.getFollower(save = False)
        for following in my_following_list:
            bio, no_of_post, no_of_follower, no_of_following, image_captions = myprofile.getProfile(following)
            bio_list.append(bio)
            no_of_post_list.append(no_of_post)
            no_of_follower_list.append(no_of_follower)
            no_of_following_list.append(no_of_following)
            image_captions_list.append(image_captions)
        for follower in my_followers_list:
            bio, no_of_post, no_of_follower, no_of_following, image_captions = myprofile.getProfile(follower)
            bio_list.append(bio)
            no_of_post_list.append(no_of_post)
            no_of_follower_list.append(no_of_follower)
            no_of_following_list.append(no_of_following)
            image_captions_list.append(','.join(image_captions))

        connection_type = ["following"] * len(my_following_list) + ["follower"] * len(my_followers_list)
        df =  pd.DataFrame({
            "bio" : bio_list,
            "no_of_post" : no_of_post_list,
            "no_of_follower" : no_of_follower_list,
            "no_of_following" : no_of_following_list,
            "image_captions" : image_captions_list,
            "connection_type" : connection_type,
            })
        df.to_excel("Dataset.xlsx", index=False)


def main():
    with open('credential.json', 'r') as f:
    creds = json.loads(f.read())
    username = creds['instagram_username']
    password = creds['instagram_password']
    session = getinsta(username, password)
    datset = Dataset(session)
    datset.genDataset(username)
    session.close()

if __name__ == "__main__":
    main()



