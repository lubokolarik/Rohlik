*** Settings ***
Library    SeleniumLibrary
Library    BuiltIn

*** Variables ***
${BROWSER}    chrome
${BASE_URL}    https://www.rohlik.cz
${ROHLICEK_URL}    https://www.rohlik.cz/rohlicek
${EMAIL}    kolarik.lubo@gmail.com
${PASSWORD}    TestujemHesloRohlicek.23456
${CHILD_NAME}    Test Child
${CHILD_BIRTH_DATE}    17. 5. 2020

*** Keywords ***
Open Rohlik Homepage
    Open Browser    ${BASE_URL}    ${BROWSER}
    Maximize Browser Window
    Wait Until Element Is Visible    data-test=header-user-icon

Login To Rohlik
    Click Element    data-test=header-user-icon
    Wait Until Element Is Visible    id=email
    Input Text    id=email    ${EMAIL}
    Input Text    id=password    ${PASSWORD}
    Click Element    data-test=btnSignIn
    Sleep    2s    # Wait for login to complete

Navigate To Rohlicek
    Go To    ${ROHLICEK_URL}
    Wait Until Element Is Visible    xpath=//button[contains(text(), 'Stát se členem')]

Click Become Member Button
    Wait Until Element Is Visible    xpath=//button[contains(text(), 'Stát se členem')]
    Click Element    xpath=//button[contains(text(), 'Stát se členem')]

Select Child Under 12
    Wait Until Element Is Visible    xpath=//button[contains(text(), 'Mám dítě do 12 let')]
    Click Element    xpath=//button[contains(text(), 'Mám dítě do 12 let')]

Select Girl Gender
    Wait Until Element Is Visible    xpath=//button[contains(text(), 'Holka')]
    Click Element    xpath=//button[contains(text(), 'Holka')]

Fill Child Details
    Wait Until Element Is Visible    xpath=//input[@placeholder='Jméno']
    Input Text    xpath=//input[@placeholder='Jméno']    ${CHILD_NAME}
    Wait Until Element Is Visible    xpath=//input[@placeholder='Datum narození']
    Input Text    xpath=//input[@placeholder='Datum narození']    ${CHILD_BIRTH_DATE}

Complete Registration
    Wait Until Element Is Visible    xpath=//button[contains(text(), 'Registrovat se')]
    Click Element    xpath=//button[contains(text(), 'Registrovat se')]

*** Test Cases ***
Register Child Account On Rohlik
    Open Rohlik Homepage
    Login To Rohlik
    Navigate To Rohlicek
    Click Become Member Button
    Select Child Under 12
    Select Girl Gender
    Fill Child Details
    Complete Registration 