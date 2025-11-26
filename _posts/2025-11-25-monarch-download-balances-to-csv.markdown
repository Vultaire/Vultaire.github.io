---
layout: post
title:  "Monarch experiments part 2: Downloading balance histories into a joint CSV"
date:   2025-11-25 18:26:00 -0800
categories: monarch python selenium
---

# Summary

This is part 2 in a multi-part series about doing custom rendering of one's net worth history based upon exports of balance history from Monarch.

In this post I discuss one possible way to pull balance histories from all of one's accounts - including closed accounts - and how to merge them into a single joint CSV file.

# Pulling balance histories from Monarch

Unfortunately, Monarch does not (yet?) provide a single file export of all your accounts' balance histories.  Combined with the limited date range options on the net worth graphs, it leaves me in the situation where I want to get a combined CSV for rendering graphs elsewhere, but it's not easy to do this.

Now, I have addressed this - I've written a Selenium script which semi-automates the process.  Just to ease the process for others who are Python-savvy, I will share some select portions of my code just to spare the effort of figuring out the exact process and CSS selectors needed to walk all the accounts (including hidden ones) and download all the balance files.  Due to the sensitive nature of automating a browser that's accessing a finance-related web site, I will not share the whole script.  I will only share specific pieces and share the context where they could be used, but stitching them together into a script is left as an exercise to the reader, and under the condition that there is NO WARRANTY OF ANY KIND on this code.

Separately - I have another script which will stich together the CSV files into a single CSV.  That script operates purely on the balance data, and that is less of a security concern, so I will share that script in full.

Using these two approaches together, it is possible to set up a process by which you can get a merged CSV file in maybe about a minute's time, rather than having to painstakingly download the files one-by-one and merge them together by hand or similar.

# Code license and explicit declaration of NO WARRANTY

Both the snippets of the Selenium script and the full CSV merge script
are provided for free under the terms of the
[GNU Public License version 3](https://www.gnu.org/licenses/gpl-3.0.txt).

Part of this license's text is the declaration that the code is being made available
to use, modify, share, etc. under the terms of the license for free, but that there
is no form of guarantee or warranty of any kind.  There may be bugs, broken edge
cases, etc., but even so, there's no promise of support or that the code will even
work.

I do not need to share this code, but am doing so in the hope that some people find
it useful, and also the hope that it puts some gentle pressure on Monarch to
eliminate the need for these tools - which may also secure me as a longer-term
customer.

# Automating downloading of balances using Selenium

## Tooling used (prerequisites)

These are the dependencies that I used for my personal script:

* **Python 3**.  I'm using Python 3.12.10 in this case, but I suspect Python 3.6+ or 3.7+ may also work.  The code snippet shared here should work on Windows, Linux, and Mac, but have not been explicitly tested on all of these.
* **The selenium Python library, version 4.33.0**.  Selenium is a library focused on browser-based testing, but it can be used for general browser automation as well.
* **Firefox**.  I've been going back and forth between browsers, and I'm tending towards Firefox again as I've been getting somewhat annoyed with Google.  I've also found that geckodriver, the program which provides the interface between Selenium and Firefox, works a bit more nicely with less breakage than chromedriver or similar.  I can open a devtools session without it messing up the automation, better allowing me to do live experimentation and more effectively write my scripts.
* **[geckodriver v0.36.0](https://github.com/mozilla/geckodriver/releases/tag/v0.36.0)**, as already described in the previous bullet.

Even if you don't want to use Firefox, these snippets are likely a good starting point for a
Chrome- or Edge-based solution, and may even work without modification as the APIs provided by
the various webdriver classes are very similar.

## The plain-text description of my own script

In my full version of the script, it does the following:

* Prepares a download directory (current_monarch_balances, based in the current working directory where the script is run from) to receive the downloaded CSV files.  If the directory already exists, it will be removed and freshly created as an empty directory.
* Launches a Selenium webdriver section and navigates to the login page.
* Waits for the user to **manually** input their credentials.  This both simplifies the program by not having to deal with 2FA or captchas, and it makes it more secure by simply not touching credentials at all.
* Once the user logs in, and presses Enter on the script which has been patiently waiting for them to log in, it will:
  * Navigate to the accounts page.
  * Expand all the hidden account drawers on that page.
  * Pull the links to all of their per-account pages.
  * Walk through those links, and for each one of them:
    * Open the menu containing the "Download balance history" action.
    * Programatically click the "Download balance history" menu item.
    * Wait for the download to complete.

The end result is a directory containing one CSV file per each of your accounts registered in Monarch,
including closed accounts, for the purpose of generating an as-complete-as-possible data set for graphing.

## Excerpts

Again, I won't provide the whole script, but I will provide some excerpts which can be used to allow you to more quickly write an automation script for this.
Hopefully this is helpful to someone.

### expand_hidden_account_drawers() - expand the hidden account drawers on the accounts page

For running on <https://app.monarch.com/accounts>, i.e. the accounts page showing your overall net worth graph.

Here there is some complexity which should be explained for the sake of those who aren't used to Selenium or web development.

I use a CSS selector - a special string which allows us to programatically find particular components of a web page - to identify all the show/hide toggles on the page for hidden accounts.  Or more accurately - I wait for those elements to be rendered to the page (since they may not be immediately available), and then I go through each element and programatically click it.  This results in each drawer being expanded and the rows inside being rendered, allowing our next function to work properly.

If you're curious about what the CSS selector does: I'm finding page elements related to the account groupings on the page (the first part of the selector), and within those elements I'm finding the show/hide toggles, if any exist.

```python
def expand_hidden_account_drawers(driver):
    element_selector = 'div[class^="AccountGroupCard__Root-"] div[class*="ShowHideToggleDrawer__Button"]'
    wait = WebDriverWait(driver, timeout=10)
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, element_selector)))
    hidden_account_drawers = driver.find_elements(By.CSS_SELECTOR, element_selector)
    for hidden_account_drawer in hidden_account_drawers:
        hidden_account_drawer.click()
```

### get_account_links() - pull the URLs for each individual account's details page

Also for running on <https://app.monarch.com/accounts>, i.e. the accounts page showing your overall net worth graph.

Again, we use a CSS selector to find elements of the page.  In this case, we again find the page elements related to the account groupings, and within those, I find all of the hyperlinks beginning with "/accounts/details/".  Based upon my examination of these links in my own Monarch account, these links appear to be all the links to the individual account pages.

For each of the hyperlinks we find: we grab the link, so we can tell our code to go to those pages later.

```python
def get_account_links(driver):
    account_a_elems = driver.find_elements(
        By.CSS_SELECTOR,
        'div[class^="AccountGroupCard__Root-"] a[class^="AccountListItem"][href^="/accounts/details/"]')
    account_links = [a.get_attribute("href") for a in account_a_elems]
    return account_links
```

### download_balances_from_monarch()

For running on the individual account details pages, using the URLs returned from get_account_links().

Here we use the passed-in URL for a specific account and open it, wait for the menu to be rendered, open the menu, find the "download balance history" option, and click it.  We use a helper function to do the click so that we can track our downloaded file count before the click and wait until the new file is downloaded properly.

The CSS probably doesn't need explanation at this point, but I'll do so anyway.  We have one pattern for finding the menu button, and then another pattern which finds the pop-up menu after it expands, then grabs all the menu items within it.

A helper function is used to perform the download; I will explain that in the next section.

```python
def download_balances_for_account(driver, account_link):
    # driver.get() unfortunately triggers a full page reload, which is a little inefficient -
    # but it will also avoid us having to repeatedly go back to the main accounts page to
    # re-enumerate the links, so it's a tradeoff I'm willing to pay.
    driver.get(account_link)

    menu_selector = 'button[class*="AccountDetailControls__EditButton-"]'
    menu_item_selector = 'div[class^="Popper__Root-"] div[role="menuitem"]'

    wait = WebDriverWait(driver, timeout=10)
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, menu_selector)))

    driver.find_element(By.CSS_SELECTOR, menu_selector).click()
    menu_elements = driver.find_elements(By.CSS_SELECTOR, menu_item_selector)
    download_balances_element = [e for e in menu_elements if e.text.strip().lower() == "download balance history"][0]
    handle_download_click(download_balances_element)
```

### handle_download_click() - Work around Selenium limitations about detecting when downloads are done

There's a little bit of complexity here because Firefox doesn't tell our Python code when it's downloading files, nor when it completes the downloads.  Instead, we observe the contents of the download directory to judge when the downloads have completed.

If it weren't for this, this would literally just be a matter of clicking the element - but if we don't wait, we will likely navigate away from this page before the download even starts.

The code calls a helper function to count the files in the download directory both before and after the click.  Until we see a new file show up - or until 5 seconds have passed without downloading the file - we'll keep re-checking the download directory for the new file.

The timeout is effectively hard-coded at 5 seconds for now.  This was good enough for my purposes, but you may change this if you get errors due to it timing out too fast.

```python
def handle_download_click(download_balances_element, timeout=5):
    # This requires special handling.
    # We need to count that there's been a change in the number of files we have downloaded.
    downloaded_before = get_downloaded_files()

    download_balances_element.click()

    start_time = time.time()
    while time.time() < start_time + timeout:
        downloaded_after = get_downloaded_files()
        if len(downloaded_after) > len(downloaded_before):
            break
    else:
        raise RuntimeError('Timeout waiting for file download')
```

### get_downloaded_files() - count the fully downloaded files in a directory

This is a very simple algorithm - Firefox-specific - for pulling the set of downloaded files in the download directory.  It works for our purposes since all the files we download will end with ".csv".  ".part" files, which is what Firefox will use to save files while being downloaded, will be ignored until they are renamed to their final file names after download completion.

If you want to run this on Chromium, Google Chrome, Edge or others, you may want to change this.  Indeed, perhaps I should even change this to match on ".csv" instead of excluding on ".part" - but for now, this is what it is, and it works well enough for this Firefox-specific script.

```python
def get_downloaded_files():
    # Important: Firefox uses ".part" extension to mark in-progress files; we won't count them.
    return [f for f in DOWNLOAD_DIR.iterdir() if f.suffix != '.part']
```

## The merge_balances script

I wrote a quick-and-dirty script - originally AI-generated, but rewritten to simplify
it and make it more suitable for sharing - which will take in a directory of CSV
values in the format that Monarch uses for balance histories and merge them together
into a single joined CSV file.  It's not the most efficient - but it works for me.

This is a bit safer for me to share, so I will provide the script in full - again,
under GPLv3 with no warranty/guarantees of any kind.

You can download it directly from GitHub here:
[merge_balance_csvs.py](https://github.com/Vultaire/Vultaire.github.io/tree/main/_posts/assets/scripts/merge_balance_csvs.py)

## Conclusion

My hope is that these resources can help you to create a merged balance history CSV file, whether or not you use the Selenium portions.
This will be used in future posts on this subject where we experiment with graphs for this data, again to fill in the feature gap or
perhaps to go beyond what Monarch or other sites are likely to provide in their sites for graphing this data.

My next post will focus specifically on Google Docs, and I will share a template which
you can clone to your personal Google account, add your data and get a flexible net
worth graph.

And @Monarch: Again, please consider making my work unnecessary and implement something here to make the net worth view more flexible,
and also consider a joint balance history download feature as well.