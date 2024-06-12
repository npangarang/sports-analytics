import pandas as pd
from selenium import webdriver
from scrapers.utils.secrets import UNDERDOG_USER, UNDERDOG_PASS
from scrapers.utils.selenium_configs import SELENIUM_CONFIGS
from selenium.webdriver.common.by import By

import time

class UnderdogScraper:
    """
    A web scraper for collecting odds data from Underdog Fantasy's Pick'em games.
    
    Attributes:
        browser (webdriver.Chrome): The Selenium WebDriver used to automate browser actions.
        odds_data (dict): Dictionary to store odds data scraped from different sports.
        converted_odds (bool): Flag to track if odds have been converted to a different format.
        platform (str): Platform name from where the data is being scraped.
        authenticated (bool): Flag to check if the user has logged in.
        current_bets (DataFrame or bool): Stores current bets data or False if no data has been fetched yet.
    """
    def __init__(self, authenticated=False, testing=False):
        """
        Initializes the UnderdogScraper with options for testing and authentication status.
        
        Parameters:
            authenticated (bool): Set True if the user session should be considered authenticated at initialization.
            testing (bool): Set True to use default WebDriver configuration; use headless configs otherwise.
        """
        options = None if testing else webdriver.ChromeOptions()
        self.browser = webdriver.Chrome(options=options)
        self.browser.get("https://underdogfantasy.com/pick-em/higher-lower/all")
        
        self.odds_data = {}
        self.converted_odds = False
        self.platform = "Underdog Fantasy"
        self.authenticated = authenticated
        self.current_bets = False
        
    def login(self):
        """
        Logs into the Underdog Fantasy website using credentials.
        """
        username = self.browser.find_elements(By.CSS_SELECTOR, '.styles__field__OeiFa')[0]
        username.send_keys(UNDERDOG_USER)
        password = self.browser.find_elements(By.CSS_SELECTOR, '.styles__field__OeiFa')[1]
        password.send_keys(UNDERDOG_PASS)
        self.browser.find_element(By.CSS_SELECTOR, 'button[data-testid="sign-in-button"]').click()
        self.authenticated = True
        
    def navigate_to_page(self, sport):
        """
        Navigates to a specific sport page on Underdog Fantasy.
        
        Parameters:
            sport (str): The sport type to navigate to (e.g., "basketball").
        """
        url = f"https://underdogfantasy.com/pick-em/higher-lower/all/{sport}"
        self.browser.get(url)
        time.sleep(3)  # TODO: consider using WebDriverWait in future
        
    def scrape_odds(self, sports=None):
        """
        Scrapes odds data for specified sports and stores them in the odds_data attribute.
        
        Parameters:
            sports (list): List of sports to scrape odds for.
        """
        if sports is None:
            sports = []
        
        for sport in sports:
            self.navigate_to_page(sport)
            # Expand all sections to ensure all odds are visible
            for expand_btn in self.browser.find_elements(By.CLASS_NAME, 'styles__toggleButton__jrfS7'):
                expand_btn.click()
                
            # Scrape odds information from each expanded section
            events = self.browser.find_elements(By.CSS_SELECTOR, '.styles__actualTopRow__qe0VJ, .styles__overUnderListCell__tbRod')
            all_lines = []
            curr_event = {}
            for event in events:
                line_info = event.text.split('\n')
                if not line_info[0][0].isdigit():
                    # This handles events currently live
                    curr_event['player'] = line_info[0]
                    curr_event['game'] = line_info[1]
                    curr_event['time'] = 'LIVE' if len(line_info) == 2 else line_info[2]
                    continue
                else:
                    event_line = curr_event.copy()
                    event_line['line'], event_line['event'] = line_info[0].split(' ', maxsplit=1)
                    event_line['type'] = "scorcher" if line_info[-1][0].isdigit() else "both"
                    all_lines.append(event_line)
            
            # Convert to DataFrame and store
            all_lines_df = pd.DataFrame(all_lines)
            self.odds_data[sport] = all_lines_df
            print(f"Found {len(all_lines_df)} upcoming {sport} events on {self.platform}.")
            
    def fetch_current_bets(self):
        """
        Fetches and stores information on current bets from Underdog Fantasy.
        """
        self.browser.get('https://underdogfantasy.com/live/pick-em')
        # Expand bet sections to view all current bets
        for expand_btn in self.browser.find_elements(By.CLASS_NAME, 'styles__topRow__q6gER'):
            expand_btn.click()
        
        all_lines = []
        # Scrape current bet data
        for event in self.browser.find_elements(By.CLASS_NAME, 'styles__overUnderLiveResultCell__PXEQT'):
            parts = event.text.split('\n')
            player, line_text, game_info = parts[0], parts[1], parts[2]
            line_val, market = line_text.split(' ')[1], " ".join(line_text.split(' ')[2:])
            game, time = game_info.split(' - ')
            
            line_info = {
                'player': player,
                'game': game,
                'time': time,
                'line': line_val,
                'event': market,
                'type': 'both'
            }
            all_lines.append(line_info)
        
        # Convert to DataFrame and update attribute
        current_bets_df = pd.DataFrame(all_lines)
        self.current_bets = current_bets_df