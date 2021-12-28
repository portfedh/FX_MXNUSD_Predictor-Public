# USD/Mexican peso official exchange rate predictor

## What it does

The script determines the USD:MXN official exchange rate for the current month and predicts the official rate (FX Obligaciones)for the next 2-4 days. 

For the script to work, it must be executed after 12:30pm of  Mexico City time. 

Steps:

- The user executes the script. 

- The script connects to the Bank of Mexico (Banxico) API. 

- It requests the FX rates for the month (FIX and Obligaciones).

- Using the FIX rate, it calculates the official exchange range for the next two to four days, depending on when its executed:

	- If its executed on a friday, it will predict the next 4 days.

	- If its executed on a saturday, it will predict the next 3 days.

	- If its executed on Monday through Thursday, or on Sunday, it will calculate the next 2 days.

- It then outputs the FX rates for the month in the terminal window.

### How to Install

To use this script, you must have previously installed:

- Python 3
- Pandas
- Requests

A (free) API token from Banxico is needed. It can be downloaded here:
[API Banxico](https://www.banxico.org.mx/SieAPIRest/service/v1/)

Substitute the API token in the Token variable:

```python
# Before
token = os.environ.get("token_banxico")

# After
token = "<paste_token_here>"
```

You can then run the python script from your terminal.


## How to Use

Simply execute the script. 

Make sure you are executing it 12:30pm or later, or the FX for future dates will be calculated incorrectly.

Output will display the FX rates for the current month and the next 2-4 days.

## Use cases

The script may be useful for accountants,  administrative/financial professionals or anyone interested in using official FX rates.

The Bank of Mexico issues 3 types of USD:MXN exchange rates:

- FIX
- DOF
- Obligaciones

FIX: is calculated by taking the average price of all trades up to 12pm. It is used mainly for transactions that an official rate closer to the spot rate.

DOF: (Diario Oficial de la Federacion). The Fix rate is published the next day in the DOF, which is where the Mexican Government makes official publications. Some institutions use DOF rate because its rate can be known beforehand from the FIX rate and can give enough time to prepare for a transaction.

Obligaciones: This rate is the FIX rate from two day prior. It also sets an official FX rate for weekends, hollidays or any non tradable days, where FIX or DOF may not be available. It is the rate used for tax purposes and in dealings with any government institutions in Mexico.

**The prediction is commonly used for tax purposes. Mexican companies or individuals holding foreign currency must calculate the value of the currency in Mexican Pesos at the beggining and end of the month and  pay tax on the gain on a monthly basis.**

**Being able to predict the official FX for the next 2-4 days may be useful to buy or sell the amount of foreign currency held to minimize the tax due at the end of each month.**

## Contributing

Help making the scripto into an executable file for windows and mac would be very helpful. 