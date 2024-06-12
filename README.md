# Sportsbetting and Analytics (WIP)
As a life-long tennis player, gym-rat, and general sports-lover who likes writing Python code and is interested in algorithmic sportsbetting, I've put together this repo to share my insights and analyses.

## +EV betting bot for UnderdogFantasy
> *+EV (positive expected value) betting* involves placing bets where the long-term expected return is greater than the amount wagered, based on the probability of the outcome and the payout offered.
This strategy focuses on identifying opportunities where the odds provided by the books are favorable, allowing bettors to achieve long-term profitability by consistently making bets that have a mathematical edge. [Here is a good example](https://oddsjam.com/betting-education/positive-expected-value-betting). This mathematical edge exists because sportsbooks often set their own lines independent of each other. As long as discrepancies like this exist, opportunities to find high-value, profitable bets exist as well.

To see if this technique really is profitiable, I developed a bot which finds +EV opportunities on the popular DFS sportsbook, [Underdog Fantasy](https://underdogfantasy.com/) by using the odds from another popular sportsbook, [Pinnacle](https://www.pinnacle.com/en/), as the baseline *true market odds*. I chose Pinnacle because it is renowned as one of the *sharpest* bookmakers in the world. Nonetheless, this is still a noteworthy assumption because nobody truly knows that the ture market odds are.

Check out `experiments/UF_PinnaclePlusEV.ipynb` to see this bot in action. It leverages scrapers that I've defined in `scrapers/`.

**Note**: For this to work, you must add your own UnderdogFantasy login credentials to the global variables in `scrapers/utils/secrets.py`

## ATP Tennis Analysis
Miscellaneous analyses on ATP Tennis data can be found in `experiments/ATP_Analysis.ipynb`. 

