*** Settings ***
Library    String
Library    SeleniumLibrary
Library    OperatingSystem
Library    Process
Library    Collections

Variables  ../Locators/Common.yaml
Variables  ../../config.yaml

*** Variables ***
${DOWNLOAD_PATH}  ${EXECDIR}/tests/Downloads

*** Keywords ***
Open the Browser headless
    [Arguments]  ${URL}
    ${chrome_options} =     Evaluate    sys.modules['selenium.webdriver'].ChromeOptions()    sys, selenium.webdriver

    Call Method    ${chrome_options}    add_argument    --no-sandbox
    Call Method    ${chrome_options}    add_argument    --disable-dev-shm-usage

    IF    "${config.environment}" != "local"
        Log   Running locally
        Call Method    ${chrome_options}    add_argument    --headless
        Call Method    ${chrome_options}    add_argument    --disable-gpu
    ELSE
        Log   Running in docker
    END

    ${prefs}=    Create Dictionary    download.default_directory=${DOWNLOAD_PATH}
    Call Method    ${chrome_options}    add_experimental_option    prefs    ${prefs}
    Create Webdriver    Chrome    options=${chrome_options}
    Set Window Size    1920    1080
    Go To  ${URL}

Init failure scenario
    Register Keyword To Run On Failure  Take screenshot on failure

Get Default Download Path
    ${platform}=    Evaluate    sys.platform    sys
    Run Keyword If    "${platform}" == "win32"    Set Variable    ${home_dir}    ${ENV:USERPROFILE}
    ...    ELSE    Set Variable    ${home_dir}    ${ENV:HOME}
    ${download_path}=    Set Variable    ${home_dir}${/}Downloads
    [Return]    ${download_path}

Take screenshot on failure
    ${screenshot_index}=    Get Variable Value    ${screenshot_index}    ${0}
    Set Global Variable    ${screenshot_index}    ${screenshot_index.__add__(1)}
    ${time}=    Evaluate    str(time.time())    time
    Capture Page Screenshot    ${SUITE_NAME}-selenium-screenshot-${time}-${screenshot_index}.png

User input email and password
    Wait Until Element Is Visible  ${login.username}  10s
    Wait Until Element Is Visible  ${login.username}  10s
    Press Keys  ${login.username}  ${config.username}
    Input Text  ${login.password}  ${config.password}

User clicks on sign in button and logins in page
    Assert click element visible  ${login.sign_in}  10s
    Assert element visible   ${main_menu.notification_bell}  10s
    sleep  1s

Open web
    Open the Browser headless  ${config.url_test}
    Assert click element visible   ${login.sign_button}  10s
    User input email and password
    User clicks on sign in button and logins in page
    Init failure scenario

Assert element visible
    [Arguments]  ${locator}  ${timeout}
    Wait Until Element Is Visible  ${locator}  ${timeout}

Assert element not visible
    [Arguments]  ${locator}  ${timeout}
    Wait until element is not Visible  ${locator}  ${timeout}

Assert click element visible
    [Arguments]  ${locator}  ${timeout}
    Wait Until Page Contains Element   ${locator}  ${timeout}
    Wait Until Element Is Visible  ${locator}  ${timeout}
    click element  ${locator}

Assert insert element visible
    [Arguments]  ${locator}  ${timeout}  ${text}
    Wait Until Element Is Visible  ${locator}  ${timeout}
    Input Text  ${locator}  ${text}

Refresh page
    Execute Javascript  location.reload();

Wait for page load
    Execute Javascript    return document.readyState === 'complete';


