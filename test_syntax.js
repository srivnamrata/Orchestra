const fs = require('fs');
try {
  new Function(fs.readFileSync('frontend/app.js', 'utf8'));
  console.log("Syntax OK");
} catch (e) {
  console.error("Syntax Error: ", e.message);
}
