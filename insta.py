from selenium import webdriver
from time import sleep
from bs4 import BeautifulSoup
import json


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

def getinsta(username, password):
    browser = webdriver.PhantomJS()
    browser.implicitly_wait(1)
    home_page = HomePage(browser)
    login_page = home_page.go_to_login_page()
    login_page.login(username, password)
    errors = browser.find_elements_by_css_selector('#error_message')
    assert len(errors) == 0
    return browser

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
        return bio, no_of_post, no_of_follower, no_of_following

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



with open('credential.json', 'r') as f:
    creds = json.loads(f.read())
username = creds['instagram_username']
password = creds['instagram_password']
session = getinsta(username, password)
myprofile = Profile(session)
bio, no_of_post, no_of_follower, no_of_following = myprofile.getProfile(username)
# myprofile.getFollowing(save = True)
# myprofile.getFollower(save = True)
session.close()
