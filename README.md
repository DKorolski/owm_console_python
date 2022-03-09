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

## 4. Execute app.py

``` 
test api connection
first run:
creates empty database file SQLite3
creates dictionary from external source for given set of cities (default - 10 cities from 200000)
on start:
check for update dictionary
retrieves forecast for sample set of cities
updates forecasts table if necessary (new dates)

```


