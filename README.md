# Book App

![Website Preview](preview.png)

## Overview
This is a simple Book App built with Node.js and Express. It allows you to manage your reading list by adding, updating, and deleting books. The app uses EJS for templating and features a clean, modern UI.

## Features
- Add a new book to your reading list
- Update book details
- Delete individual books
- Special action: Delete the last added book
- Responsive and user-friendly interface

## Project Structure
```
app.js                # Main application file
package.json          # Project dependencies and scripts
public/styles.css     # CSS styles
views/                # EJS templates
  create.ejs
  delete.ejs
  home.ejs
  update.ejs
```

## Getting Started

### Prerequisites
- Node.js (v14 or higher recommended)
- npm (Node package manager)

### Installation
1. Clone this repository or download the source code.
2. Navigate to the project directory:
   ```bash
   cd book-app
   ```
3. Install dependencies:
   ```bash
   npm install
   ```

### Running the App
Start the server with:
```bash
node app.js
```
The app will be available at `http://localhost:8080` (or the port specified in your code).

## Usage
- Click **Add a New Book** to add a book to your list.
- Use the **Update** and **Delete** buttons to manage each book.
- Use the **Delete The Last Added Book** button for a quick special action.

## Preview
See the screenshot above for a preview of the website UI.

## License
This project is for educational purposes.
