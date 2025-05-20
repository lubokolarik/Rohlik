*** Settings ***
Documentation   Settings
...  1. Open Chrome and navigate to https://www.rohlik.cz/rohlicek
...  2. Click on the "Přihlásit se" button, login button
...  3. Fill in:
...     - Email: kolarik.lubo@gmail.com
...     - passw: TestujemHesloRohlicek.23456
...  4. Login with login button "Přihlásit se"
...  6. Verify sign in notification bell, check login
...  7. Click on search
...  8. Click on first product add button to basket:
...  9. Verify basket include product included text: "V košíku máte 1"

Resource  ../resources/Keywords/Common.robot
Resource  ../resources/Keywords/Basket.robot

Suite Setup  Run keywords
...  Open web
Suite Teardown	Close Browser

*** Variables ***

*** Test Cases ***
Settings
  Add product to basket
  Check basket
  Remove product from basket  #clean basket for next test
