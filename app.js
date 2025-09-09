const express = require('express');
const path = require('path');
const app = express();
const port = 8080;

// --- In-Memory Data Store ---
let books = [
    { id: 1, title: "The Hobbit", author: "J.R.R. Tolkien" },
    { id: 2, title: "1984", author: "George Orwell" },
    { id: 3, title: "To Kill a Mockingbird", author: "Harper Lee" },
];
let nextId = 4;

// --- Middleware ---
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));
app.use(express.static(path.join(__dirname, 'public')));
app.use(express.urlencoded({ extended: true }));

// --- Routes ---

// 1. READ all books (Home Page)
app.get('/', (req, res) => {
    res.render('home', { books: books });
});

// 2. CREATE a book (Show form and handle submission)
app.get('/create', (req, res) => {
    res.render('create');
});

app.post('/create', (req, res) => {
    const { title, author } = req.body;
    const newBook = { id: nextId++, title, author };
    books.push(newBook);
    res.redirect('/');
});

// 3. UPDATE a book (Show form and handle submission)
app.get('/update/:id', (req, res) => {
    const id = parseInt(req.params.id);
    const book = books.find(b => b.id === id);
    if (book) {
        res.render('update', { book: book });
    } else {
        res.status(404).send('Book not found');
    }
});

app.post('/update/:id', (req, res) => {
    const id = parseInt(req.params.id);
    const book = books.find(b => b.id === id);
    if (book) {
        book.title = req.body.title;
        book.author = req.body.author;
    }
    res.redirect('/');
});

// 4. DELETE a book (Show confirmation and handle deletion)
app.get('/delete/:id', (req, res) => {
    const id = parseInt(req.params.id);
    const book = books.find(b => b.id === id);
    if (book) {
        res.render('delete', { book: book });
    } else {
        res.status(404).send('Book not found');
    }
});

app.post('/delete/:id', (req, res) => {
    const id = parseInt(req.params.id);
    books = books.filter(b => b.id !== id);
    res.redirect('/');
});


// 5. NEW: DELETE the book with the HIGHEST ID
app.post('/delete-highest-id', (req, res) => {
    // If there are no books, do nothing and just redirect.
    if (books.length === 0) {
        return res.redirect('/');
    }

    // Find the highest ID.
    // Math.max(...[1, 2, 3]) will return 3.
    const maxId = Math.max(...books.map(book => book.id));

    // Filter the books array, keeping only the books that DON'T have the highest ID.
    books = books.filter(book => book.id !== maxId);

    // Redirect back to the homepage to show the updated list.
    res.redirect('/');
});


// --- Start the Server ---
app.listen(port, () => {
    console.log(`🚀 Server is running at http://localhost:${port}`);
});
