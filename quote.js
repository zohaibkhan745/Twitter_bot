const fs = require("fs");

function randomQuote() {
  fetch("https://quotes-api-self.vercel.app/quote")
    .then((response) => response.json())
    .then((data) => {
      let quoteText = data.quote + " ~" + data.author + "\n";

      // Write to quote.txt
      fs.appendFileSync("quotes.txt", quoteText);
      console.log("Quote saved to quote.txt ✅");
    })
    .catch((error) => console.error(error));
}

randomQuote();
