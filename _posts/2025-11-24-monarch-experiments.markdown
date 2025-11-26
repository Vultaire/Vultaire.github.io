---
layout: post
title:  "Monarch experiments part 1: Preamble"
date:   2025-11-24 21:13:00 -0800
categories: monarch
---

# Summary

In this post I summarize:

* Why I switched from Empower to Monarch
* The shortcomings I see so far with Monarch's UX
* Possible workarounds for these limitations

# The switch from Empower to Monarch

For personal purposes I recently switched to using Monarch, after 8 years of using the Personal Capital dashboard (which was bought out by Empower some time ago).  It was a great free tool, but Empower recently decided to discontinue it and migrate everyone to their new Empower Retirement dashboard - which, I'm sorry to say, to me seems like a bug-ridden mess.  Or if I put things more nicely - the cutover was too soon; there's far too many issues with the new dashboard.

While I did not seem to have significant problems with lost data that some users apparently reported, post-migration I have had significant connectivity issues with no way to resolve them, and the new UI has been buggy and unhelpful.  Combined with the fact that I'm not a paying customer and don't want to deal with the upsell nags - I'm a Boglehead and unlikely to sign on to active management - I looked at alternatives and settled on [Monarch Money](https://monarch.com/referral/aau4r4kw0s?r_source=copy) (referral link).  I decided that since I don't see a good free option at this point that this type of app provides enough value that for me it's worth paying for.

Monarch has been pretty nice.  It has a nice, easy to use interface, and while I wasn't planning on using it for transaction tracking/categorization, I have ended up using that functionality somewhat.  It syncs with all of my accounts, including ones I had to handle as manual accounts in Personal Capital.  And I can import historic transactions and balances, allowing me to create a fuller historic picture of my family's finances over time, which I personally find value in even if it's not so practically vital.  I haven't found this feature set in any free alternatives, so I've decided to stick with Monarch at least for one year.

# The pain points

All the above being said, Monarch has its pain points as well.  Most are minor annoyances in my opinion, but there's a few that stand out.

The net worth view is generally very nice, but it's anchored on the present day and only provides canned ranges of time to look back - 1/3/6 months, year-to-date, 1 year, or all time.  For the main purposes of Monarch this is probably sufficient.  However, I enjoyed extra flexibility with Personal Capital's solution.  I liked the ability to zoom in on particular times, or to check my rate of return in previous years compared to the current, but Monarch is not as flexible in this regard.  I sincerely hope that they will improve this; this is the single biggest pain point to me with Monarch and a fix for this alone would likely allow me to just "settle in" to using this long-term.

The other thing I'd like to have would be having buttons to click on my accounts to quickly toggle inclusion in the net worth graph - that's not something that Empower even gave to me, but I would love to have that as well.

Reddit seems to think that Monarch is slow to respond to these types of user requests - I don't really want to judge here as a new user, plus I've no idea how large the development team is and such.  So while I hope they will move on this, I decided I wanted to experiment with what was possible myself.

One of the great things of Monarch is that you can easily pull your data out.  Want to pull all your transactions out?  Piece of cake.  Want to correct something in the past?  You have options, going as far as doing a full transaction export and rewriting history - something you couldn't do in Empower.  Account balances?  Also doable, even if not quite as easy since you have to pull them per account.  (@Monarch: If you can add a combined CSV dump of balances of the form `Date,Account #1[,Account #2,...]`, that would seriously make my day!)

# How to address this

I have many accounts - my checking, my savings, my retirement accounts, my kids' 529's, and even some manually tracked assets such as my cars and my house.  If I want to pull all my balance data for doing my own net worth graph - and if I want to pull my historic accounts as well which have been closed but contribute to the overall graph - it's a lot of work to pull each of the CSVs, then merge them together into a joint CSV across the full span of time I've had these accounts open (and have corresponding data for them).

From there, once I have them in a joint CSV file, I have many options.

I have already successfully done this - co-written a Selenium script to pull the CSV files, vibe coded (ugh...) a quick and dirty CSV merge tool, and created a Google Sheet which allows me to more-or-less reproduce the type of flexibility I had with Empower for the net worth graph.  While not as pretty, it works and is actually more functional - but it is a hassle since I have to pull the data out of Monarch to do it.

@Monarch: If anyone is reading this, please consider addressing these concerns!  I did also formally request these particular features via your request board site as well, for what it's worth.

Anyway, in my next post: I'll cover how to use Python, Selenium and Firefox to pull CSV data from all of my Monarch accounts and merge them into a joint CSV file.
