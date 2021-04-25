var template = require("./../templates/job-item.handlebars");

$(function () {
  $.get("/api/jobs/", function (data) {
    for (let index in data) {
      const job = data[index];
      const html = template(job);
      $("#job_list").append(html);
    }
  });
});

