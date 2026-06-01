document.addEventListener("DOMContentLoaded", function() {
    var modal = document.getElementById("myModal");
    var openModalBtn = document.getElementById("openModalBtn");
    var closeModalBtn = document.getElementsByClassName("close")[0];
    var mainInput = document.getElementById("mainInput");
    var filterInput = document.getElementById("filterInput");
    var listContainer = document.getElementById("listContainer");
    var listItems = listContainer.getElementsByClassName("list-item");

    openModalBtn.onclick = function() {
        modal.style.display = "block";
        filterInput.value = ""; // Clear filter input when opening modal
        filterList(""); // Show all items initially
    }

    closeModalBtn.onclick = function() {
        modal.style.display = "none";
    }

    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    }

    for (var i = 0; i < listItems.length; i++) {
        listItems[i].onclick = function() {
            var value = this.getAttribute("data-value");
            selectedValue = this.textContent || this.innerText;
            mainInput.value = value;
            modal.style.display = "none";
        }
    }

    filterInput.onkeyup = function() {
        var filter = filterInput.value.toLowerCase();
        filterList(filter);
    }

    function filterList(filter) {
        for (var i = 0; i < listItems.length; i++) {
            var item = listItems[i];
            var text = item.textContent || item.innerText;
            if (text.toLowerCase().indexOf(filter) > -1) {
                item.style.display = "";
            } else {
                item.style.display = "none";
            }
        }
    }
});
