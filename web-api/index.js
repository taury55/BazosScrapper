const express  = require('express');
const bodyParser = require('body-parser');
const mysql = require('mysql');
const config = require('../config.json');

const app = express();
const port = process.env.PORT || 4051;

const con = mysql.createConnection({
	host: config.host,
	user: config.user,
	password: config.password,
	database: config.database
});

con.connect(function(err) {
	if (err) throw err;
});

app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

app.get('/', (_, res) => {
	res.send("Scrapper API server welcomes you.");
});

app.get('/scrappings', async function (req, res) {
	const sql = `SELECT * FROM scrapping`;
	con.query(sql, (err, rows) => {
		if (err) {
			console.log("error: ", err);
		} else {
			res.send(rows);
		}
	});
});

app.get('/set-as-seen/:itemId', async function (req, res) {
	const sql = `UPDATE inzerat SET seen='1' WHERE id=?`;
	con.query(sql, [req.params.itemId], (err, rows) => {
		if (err) {
			console.log("error: ", err);
		}
	});

	res.redirect(req.get('referer'));
});

app.get('/get-inzeraty/:itemId', async function (req, res) {
	const sql = `SELECT * FROM inzerat WHERE scrappingId=?`;
	con.query(sql, [req.params.itemId], (err, rows) => {
		if (err) {
			console.log("error: ", err);
		} else {
			res.send(rows);
		}
	});
});

app.get('/active-scrapping/:itemId', async function (req, res) {
	var sql = `SELECT active FROM scrapping WHERE id=?`;
	con.query(sql, [req.params.itemId], function (err, result) {
		if (err) {
			console.log("error: ", err);
		} else {
			sql = `UPDATE scrapping SET active=? WHERE id=?`;
			con.query(sql, [!result[0].active, req.params.itemId], function (err, resultB) {
				if (err) {
					console.log("error: ", err);
				} else {
					console.log("Scrapping updated.");
				}
			});
		}
	});

	res.redirect('/scrapper/');
});

app.get('/del-scrapping/:itemId', async function (req, res) {
	var sql = `DELETE FROM scrapping WHERE id=?`;
	con.query(sql, [req.params.itemId], function (err, result) {
		if (err) {
			console.log("error: ", err);
		} else {
			console.log("Scrapping removed.");
		}
	});

	sql = `DELETE FROM inzerat WHERE scrappingId=?`;
	con.query(sql, [req.params.itemId], function (err, result) {
		if (err) {
			console.log("error: ", err);
		} else {
			console.log("Inzeraty removed.");
		}
	});

	res.redirect('/scrapper/');
});

app.post('/update-scrapping', (req, res) => {
	if (req.body.searchingFor.length != 0 && req.body.priceFrom.length != 0 && req.body.priceTo.length != 0) {
		const sql = `UPDATE scrapping SET
			searchingFor=?, searchingFilter=?, priceFrom=?, priceTo=?
			WHERE id=?`;
		con.query(sql, [req.body.searchingFor, req.body.searchingFilter, req.body.priceFrom, req.body.priceTo, req.body.itemId], function (err, data) {
			if (err) {
				console.log("error: ", err);
			} else {
				console.log("Scrapping updated");
			}
		});
	}

	res.redirect('/scrapper/');
});

app.post('/new-scrapping', (req, res) => {
	if (req.body.searchingFor.length != 0 && req.body.priceFrom.length != 0 && req.body.priceTo.length != 0) {
		const sql = `INSERT INTO scrapping
			( searchingFor, searchingFilter, priceFrom, priceTo, active )
			VALUES
			( ?, ?, ?, ?, ? )`;
		con.query(sql, [req.body.searchingFor, req.body.searchingFilter, req.body.priceFrom, req.body.priceTo, 1], function (err, data) {
			if (err) {
				console.log("error: ", err);
			} else {
				console.log("New scrapping added");
			}
		});
	}

	res.redirect('/scrapper/');
});


app.listen(port, () => {
	console.log(`server is running on port: ${port}`);
});
