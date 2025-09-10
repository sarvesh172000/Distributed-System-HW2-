const express = require('express');
const path = require('path');
const app = express();
const port = 8080;

// --- In-Memory Data Store ---
// We start with some sample data.
let books = [
    { id: 1, title: "The Hobbit", author: "J.R.R. Tolkien" },
    { id: 2, title: "1984", author: "George Orwell" },
    { id: 3, title: "To Kill a Mockingbird", author: "Harper Lee" },
];
// This ensures new books get a unique ID.
let nextId = 4;

// --- Middleware ---
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));
app.use(express.static(path.join(__dirname, 'public')));
app.use(express.urlencoded({ extended: true }));

// --- Main Routes ---

// READ: Display the home page with all books.
app.get('/', (req, res) => {
    res.render('home', { books: books });
});

// CREATE: Show the form to add a new book.
app.get('/create', (req, res) => {
    res.render('create');
});

// CREATE: Handle the form submission to add a new book.
app.post('/create', (req, res) => {
    const { title, author } = req.body;
    if (title && author) {
        const newBook = { id: nextId++, title, author };
        books.push(newBook);
    }
    res.redirect('/');
});

// UPDATE: Show the form to edit a specific book.
app.get('/update/:id', (req, res) => {
    const id = parseInt(req.params.id);
    const book = books.find(b => b.id === id);
    if (book) {
        res.render('update', { book: book });
    } else {
        res.status(404).send('Book not found');
    }
});

// UPDATE: Handle the form submission to update a specific book.
app.post('/update/:id', (req, res) => {
    const id = parseInt(req.params.id);
    const book = books.find(b => b.id === id);
    if (book) {
        book.title = req.body.title;
        book.author = req.body.author;
    }
    res.redirect('/');
});

// DELETE: Show the confirmation page for deleting a specific book.
app.get('/delete/:id', (req, res) => {
    const id = parseInt(req.params.id);
    const book = books.find(b => b.id === id);
    if (book) {
        res.render('delete', { book: book });
    } else {
        res.status(404).send('Book not found');
    }
});

// DELETE: Handle the confirmation to delete a specific book.
app.post('/delete/:id', (req, res) => {
    const id = parseInt(req.params.id);
    books = books.filter(b => b.id !== id);
    res.redirect('/');
});


// --- Special Action Routes ---

// UPDATE Book with ID 1 to "Harry Potter".
app.post('/update-book-one', (req, res) => {
    const bookToUpdate = books.find(book => book.id === 1);
    if (bookToUpdate) {
        bookToUpdate.title = "Harry Potter";
        bookToUpdate.author = "J.K Rowling";
    }
    res.redirect('/');
});

// DELETE the book with the HIGHEST ID.
app.post('/delete-highest-id', (req, res) => {
    if (books.length > 0) {
        const maxId = Math.max(...books.map(book => book.id));
        books = books.filter(book => book.id !== maxId);
    }
    res.redirect('/');
});


// --- Start the Server ---
app.listen(port, () => {
    console.log(`🚀 Server is running at http://localhost:${port}`);
});
