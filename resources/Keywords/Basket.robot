*** Settings ***
Library     String
Library 	SeleniumLibrary
Library    OperatingSystem
Library    Process

Variables  ../Locators/Common.yaml
Variables  ../../config.yaml

*** Variables ***

*** Keywords ***
Add product to basket
    Assert click element visible  ${main_menu.search}  10s
    Assert click element visible  ${main_menu.product_add_basket}  10s

Check basket
    Assert click element visible  ${main_menu.basket}  10s
    Assert element visible  ${main_menu.check_order}  10s

Remove product from basket
    Assert click element visible  ${main_menu.remove_product}  10s
    sleep  1s

