// Import Handlebars runtime lib
const Handlebars = require("handlebars/runtime");

Handlebars.registerHelper("ifeq", function (a, b, options) {
  if (a == b) {
    return options.fn(this);
  }
  return options.inverse(this);
});

module.exports = Handlebars;
