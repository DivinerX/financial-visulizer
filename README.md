# finance-visualizer

Last edited 9/17/2020

#### Version

Written in Python 3.7.7.

### Dependencies

**numpy** 1.19.0  
**pandas** 1.0.5  
**pygal** 2.4.0   

## What is it?

**organize.py**: A script to give a variable number of CSV files containing unorganized financial transactions which will be organized into two CSVs, one for income, and another for expenses.

**categories.py**: File where you add the expense and income categories for organize.py to use when classifying/categorizing your transactions.

**visualize.py**: A script to take the cleaned up transactions from the organize script and create SVG graphs to visualize the data. The graphs are then put in
a generated HTML file which can be opened locally in your browser.
