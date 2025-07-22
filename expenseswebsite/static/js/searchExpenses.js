// CSRF helper for Django
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const searchField = document.querySelector("#searchField");
const tableOutput = document.querySelector(".table-output");
const appTable = document.querySelector(".app-table");
const paginationContainer = document.querySelector(".pagination-container");
tableOutput.style.display = "none";
const tbody = document.querySelector(".table-body");

searchField.addEventListener("keyup", (e) => {
    const searchValue = e.target.value;

    if (searchValue.length > 0) {
        paginationContainer.style.display = "none";
        tbody.innerHTML = "";
        console.log("searchValue", searchValue);
        fetch('/search-expenses', {
            body: JSON.stringify({ searchText: searchValue }),
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie('csrftoken')
            }
        })
        .then(res => res.json())
        .then(data => {
            console.log("data", data);
            appTable.style.display = "none";
            tableOutput.style.display = "block";
            tbody.innerHTML = "";

            // If your Django view returns {data: [...]}
            const results = data.data || data;

            if (results.length === 0) {
                tableOutput.innerHTML = `<p>No Expenses Found</p>`;
            } else {
                results.forEach(item => {
                    tbody.innerHTML += `
                        <tr>
                            <td>${item.date}</td>
                            <td>${item.amount}</td>
                            <td>${item.category}</td>
                            <td>${item.description}</td>
                        </tr>
                    `;
                });
            }
        })
        .catch(error => {
            console.error('Error:', error);
            tableOutput.innerHTML = `<p>Error loading expenses</p>`;
        });
    } else {
        tableOutput.style.display = "none";
        appTable.style.display = "block";
        paginationContainer.style.display = "block";
    }
});