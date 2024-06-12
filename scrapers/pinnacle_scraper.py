from selenium import webdriver
from selenium.webdriver.common.by import By
import re
import pandas as pd
import time
# TODO: consider replacing instances of time.sleep() with WebDriverWait

class PinnaclePropsScraper:
    """
    A web scraper for collecting odds data from Pinnacle -- one of the sharpest sportsbooks.
    
    Attributes:
        browser (webdriver.Chrome): The Selenium WebDriver used to automate browser actions.
        odds_data (dict): Dictionary to store odds data scraped from different sports.
        converted_odds (bool): Flag to track if odds have been converted to a different format.
        platform (str): Platform name from where the data is being scraped.
        authenticated (bool): Flag to check if the user has logged in.
    """
    def __init__(self, testing=False):
        """
        Initializes the Pinnacle Scraper with a testing option.
        
        Parameters:
            testing (bool): Set True to use default WebDriver configuration; use headless configs otherwise.
        """
        options = None if testing else webdriver.ChromeOptions()
        self.browser = webdriver.Chrome(options=options)
        self.odds_data = {}
        self.converted_odds = False
        self.platform = "Pinnacle"
    
    def navigate_to_page(self, sport):
        """
        Navigates to a specific sport page on Underdog Fantasy.
        
        Parameters:
            sport (str): The sport type to navigate to (e.g., "basketball").
        """
        url = f"https://www.pinnacle.com/en/{sport}/matchups/"
        self.browser.get(url)
        # buffer to let events load
        time.sleep(3)
    
    @staticmethod
    def odds_to_probability(odds):
        """
        Helper to convert odds to decimal probabilities.

        :param odds (float): American odds
        :return (float): Converted odds probability
        """
        if odds > 0:
            return 100 / (odds + 100)
        else:
            return -odds / (-odds + 100)
    @staticmethod
    def scrape_props(browser):
        """
        Helper function to scrape player-prop lines from specific events

        :param browser (webdriver.Chrome): The Selenium WebDriver used to automate browser actions.
        """
        player_props = []
        for event in browser.find_elements(By.CLASS_NAME, 'style_primary__uMCOh'):
            # remove event for spacing
            line_text = event.text        
            try:
                event = re.findall(r'\((.*?)\)', line_text)[0]
            except:
                continue
            line_text = re.sub(r'\(.*?\)', '', line_text)
            line_info = line_text.split("\n")
            # print(line_info.text)
            
            player = line_info[0][:-1]
            # player = line_info.split(' (')[0]
            # edge case for hide all button
            # print(line_info)
            if (line_info[1] in ('Yes', 'No')) or line_info[2] in ('Yes' ,'No'):
                continue
            # print(line_info)
            if 'Hide' in line_text:
                over = line_info[3]
                under = line_info[5]    
                line, event = line_info[2].split(" ", maxsplit=2)[1:]
            else:
                over = line_info[2]
                under = line_info[4]
                line, event = line_info[1].split(" ", maxsplit=2)[1:]
            
            props_data = {
                'player': player,
                'event': event,
                'line': line,
                'over':int(over),
                'under':int(under)
            }
            player_props.append(props_data)
        all_props_df = pd.DataFrame(player_props)
        return all_props_df
        
    def scrape_odds(self, sports=None):
        """
        Scrapes odds data for specified sports and stores them in the odds_data dictionary.
        
        Parameters:
            sports (list): List of sports to scrape odds for.
        """
        browser = self.browser
        for sport in sports:
            self.navigate_to_page(sport)
            
            if not self.converted_odds:
                # convert to American Odds
                browser.find_element(By.CSS_SELECTOR, '.style_button__2bncQ').click()
                browser.find_element(By.CSS_SELECTOR, '.style_not-selected__1pD9N').click()
                self.converted_odds = True
                
            games = browser.find_elements(By.CSS_SELECTOR, '.style_metadata__3MrIC')
            
            all_props = []
            for i in range(len(games)):
                # Re-find the elements to avoid stale references
                games = browser.find_elements(By.CSS_SELECTOR, '.style_metadata__3MrIC')
                game = games[i]

                line_info = game.text.split('\n')
                
                if len(line_info) == 1:  # not an event
                    continue 
                
                game_name = line_info[0] + " @ " + line_info[1]
                time.sleep(2)
                # DEBUGGING HERE RIGHT NOW
                # props_df = self.scrape_props(browser)
                # props_df['game'] = game_name
                # all_props.append(props_df)
                # print(f'Scraped player props for {game_name}')
                    
                try:
                    # click event to access player props
                    game.click()
                    player_props_link = browser.current_url.replace('#all', '#player-props')
                    browser.get(player_props_link)
                    break
                    time.sleep(2)
                    # browser.find_element(By.CSS_SELECTOR, 'button[id="player-props"]').click()
                    props_df = self.scrape_props(browser)
                    props_df['game'] = game_name
                    all_props.append(props_df)
                    print(f'Scraped player props for {game_name}')
                except:
                    print(f'No player props found for {game_name}')
                
                browser.back()
                time.sleep(2)
                
            if len(all_props) == 0:
                print(f"Couldn't find any upcoming events for {sport}")
                self.odds_data[sport] = None
                continue
            
            all_props_df = pd.concat(all_props, ignore_index=True)
            all_props_df['over_prob'] = all_props_df['over'].apply(PinnaclePropsScraper.odds_to_probability)
            all_props_df['under_prob'] = all_props_df['under'].apply(PinnaclePropsScraper.odds_to_probability)
            self.odds_data[sport] = all_props_df
            print(f"Found {len(all_props_df)} upcoming {sport} events on {self.platform}.")
            
pin_scraper = PinnaclePropsScraper()
pin_scraper.scrape_odds(['basketball/nba'])