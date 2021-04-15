# finance-visualizer

## What is it?

**organize.py**: A script to give a variable number of CSV files containing unorganized financial transactions which will be organized into two CSVs, one for income, and another for expenses.

**categories.py**: File where you add the expense and income categories for organize.py to use when classifying/categorizing your transactions.

**visualize.py**: A script to take the cleaned up transactions from the organize script and create SVG graphs to visualize the data. The graphs are then put in a generated HTML file which can be opened locally in your browser.

### More info

You can pass **organize.py** a file of newline separated strings and if these strings are found in the "Extended Description" column of any of the CSVs passed in then the corresponding row will get ignored.

**organize.py** looks for three specific columns in the CSV(s) it receives: "Posting Date", "Amount", and "Extended Description". If a CSV is passed in that is missing even one of those columns then the script will throw an error and exit. These can be changed in the code to whatever columns would be most useful for you. Some things to know:

- The "Amount" column expects expenses to be negative numbers and income to be positive numbers, this is the only way the script can differentiate between income and expenses. This might have been obvious but there it is.
- The "Extended Description" column's only use is it will get checked against any exceptions you passed in and the corresponding row will be ignored if an exception is found the the column.
- The optional description that you can provide to your transactions in **organize.py** don't add anything to the visualizations at all. I personally just prefer to have descriptions in the organized transactions in case I want to look at them later.
