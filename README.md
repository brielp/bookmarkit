# BookmarkIt #

Brielle's Springboard Capstone Project #1

Deployed: 

API: LinkPreview

## Overview ##

BookmarkIt is a pinterest-like app that allows users to bookmark any url. Once saved, these bookmarks can be organized into boards, given a due date, and marked complete. BookmarkIt can be used to organize articles to read for later, and can be a great study and learning tool with built-in due dates and reminders to "complete" a bookmarked item.

## Features and Flow ##

BookmarkIt user flow is as follows: 

1. User Creates an account or logs into a previously existing account
2. A "general" board is automatically created for new users to start saving bookmarks to
3. Once a user has signed up/logged in, they are directed to a page listing all of their current boards. They have the option here to add a board, or edit/delete existing boards
4. Users can click into a board to see all of their saved posts and to save new posts
5. When a user adds a bookmark, a call is made to the LinkPreview API to create an engaging way to bookmark pages. The API returns data like the website/article title, description, and image url which is then displayed on the bookmark board. 
6. Users can optionally add a due date to a post. Two days before the due date, the user will be notified that the saved article is due soon
7. Once the user has "completed" the bookmarked content, they can mark the bookmark as complete, which will send it to the "completed" section of the board. Users can also delete or edit a post at any time.  

## Technology Used ##

BookmarkIt utilizes Python, Flask, Postgres, SQLAlchemy and WTForms on the back end with Jinja, HTML, CSS, Javascript, and Bootstrap on the front end.