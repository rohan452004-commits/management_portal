document.addEventListener("DOMContentLoaded", function () {
  var todayLabel = document.getElementById("todayLabel");
  var currentYear = document.getElementById("currentYear");
  var now = new Date();

  if (todayLabel) {
    todayLabel.textContent = new Intl.DateTimeFormat(undefined, {
      weekday: "short",
      month: "short",
      day: "numeric"
    }).format(now);
  }

  if (currentYear) {
    currentYear.textContent = now.getFullYear();
  }

  var search = document.getElementById("studentSearch");
  if (search) {
    var rows = Array.prototype.slice.call(document.querySelectorAll(".student-row"));
    var noResults = document.getElementById("noResults");
    var resultCount = document.querySelector(".result-count");

    function filterStudents() {
      var query = search.value.trim().toLowerCase();
      var visibleCount = 0;
      rows.forEach(function (row) {
        var matches = row.getAttribute("data-search").indexOf(query) !== -1;
        row.hidden = !matches;
        if (matches) visibleCount += 1;
      });
      if (noResults) noResults.hidden = visibleCount > 0;
      if (resultCount) resultCount.textContent = visibleCount;
    }

    search.addEventListener("input", filterStudents);
    document.addEventListener("keydown", function (event) {
      if (event.key === "/" && !event.ctrlKey && !event.metaKey && !event.altKey) {
        var active = document.activeElement;
        if (!active || !/INPUT|TEXTAREA/.test(active.tagName)) {
          event.preventDefault();
          search.focus();
        }
      }
    });
  }

  document.querySelectorAll(".flash-close").forEach(function (button) {
    button.addEventListener("click", function () {
      button.parentElement.remove();
    });
  });

  document.querySelectorAll(".delete-form").forEach(function (form) {
    form.addEventListener("submit", function (event) {
      var name = form.getAttribute("data-student-name");
      if (!window.confirm("Delete the record for " + name + "? This cannot be undone.")) {
        event.preventDefault();
      }
    });
  });

  var sidebar = document.getElementById("sidebar");
  var menuToggle = document.getElementById("menuToggle");
  if (sidebar && menuToggle) {
    menuToggle.addEventListener("click", function () {
      var isOpen = sidebar.classList.toggle("open");
      menuToggle.setAttribute("aria-expanded", String(isOpen));
    });
    document.addEventListener("click", function (event) {
      if (window.innerWidth <= 820 && sidebar.classList.contains("open") &&
          !sidebar.contains(event.target) && !menuToggle.contains(event.target)) {
        sidebar.classList.remove("open");
        menuToggle.setAttribute("aria-expanded", "false");
      }
    });
  }
});
