# Setup the project

## 1. Open the project folder in VS Code

## 2. In VS Code, open the Command Palette `(View > Command Palette or (Ctrl+Shift+P))`

Then select: `Python: Select Interpreter`  
Then select: `Python 3.9`  
Then select: `Python: Select Linter`  
Then select: `Flake8`

## 3. Run Terminal: `Create New Integrated Terminal (Ctrl+`))`  

``` bash
python -m venv env
env\scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
pytest
```

## 4. Execute console_app.py

``` 
test api connection
first run:
creates empty database file SQLite3
creates dictionary from external source
on start:
check for update dictionary
user dialogue:
prompts user to input city name to get forecast
returns to user city info from database
returns to user forecast brief message
updates forecasts table if necessary (new dates)

```


