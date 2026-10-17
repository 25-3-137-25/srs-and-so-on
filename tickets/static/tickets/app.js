const csrfToken = document.querySelector(
    "[name=csrfmiddlewaretoken]"
).value;

async function apiRequest(url, options = {}) {
    const response = await fetch(url, {
        ...options,
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken,
            ...(options.headers || {})
        },
        credentials: "same-origin"
    });

    let data = null;

    if (response.status !== 204) {
        data = await response.json().catch(() => null);
    }

    if (!response.ok) {
        throw new Error(
            JSON.stringify(data || {
                detail: "Ошибка выполнения запроса"
            })
        );
    }

    return data;
}

const categorySelect =
    document.getElementById("category");

const form =
    document.getElementById("ticket-form");

const titleInput =
    document.getElementById("title");

const message =
    document.getElementById("message");

function showMessage(text, isError = false) {
    message.textContent = text;
    message.className =
        "alert " + (isError ? "alert-danger" : "alert-success");
}

async function loadCategories() {
    const categories = await apiRequest(
        "/api/categories/"
    );

    categorySelect.replaceChildren();

    for (const category of categories) {
        const option = document.createElement("option");
        option.value = category.id;
        option.textContent = category.name;
        categorySelect.append(option);
    }
}

form.addEventListener("submit", async (event) => {
    event.preventDefault();

    try {
        await apiRequest("/api/tickets/", {
            method: "POST",
            body: JSON.stringify({
                title: titleInput.value,
                category: Number(categorySelect.value)
            })
        });

        titleInput.value = "";
        showMessage("Заявка успешно создана");

        await loadTickets();
    } catch (error) {
        showMessage(
            "Не удалось создать заявку: " + error.message,
            true
        );
    }
});

const list = document.getElementById("tickets-list");
const loading = document.getElementById("loading");
const filter = document.getElementById("status-filter");

async function loadTickets() {
    loading.hidden = false;

    const params = new URLSearchParams();

    if (filter.value) {
        params.set("status", filter.value);
    }

    const query = params.toString();
    const url = "/api/tickets/" + (query ? "?" + query : "");

    try {
        const tickets = await apiRequest(url);

        list.replaceChildren();

        if (tickets.length === 0) {
            const empty = document.createElement("p");
            empty.textContent = "Заявки не найдены";
            list.append(empty);
            return;
        }

        for (const ticket of tickets) {
            const row = document.createElement("div");
            row.className =
                "d-flex justify-content-between align-items-center border-bottom py-3 gap-3";

            const title = document.createElement("div");
            title.textContent =
                ticket.title + " — " + ticket.category_name;

            const status = document.createElement("span");
            status.className = "badge bg-blue-lt";
            status.textContent = ticket.status;

            row.append(title, status);
            list.append(row);
        }
    } catch (error) {
        showMessage(
            "Не удалось загрузить заявки: " + error.message,
            true
        );
    } finally {
        loading.hidden = true;
    }
}

filter.addEventListener("change", loadTickets);

async function initialize() {
    try {
        await loadCategories();
        await loadTickets();
    } catch (error) {
        showMessage(
            "Ошибка инициализации: " + error.message,
            true
        );
    }
}

initialize();
async function changeStatus(ticketId, newStatus) {
    await apiRequest(`/api/tickets/${ticketId}/`, {
        method: "PATCH",
        body: JSON.stringify({
            status: newStatus
        })
    });

    await loadTickets();
}
async function deleteTicket(ticketId, ticketTitle) {
    const confirmed = confirm(
        `Удалить заявку «${ticketTitle}»?`
    );

    if (!confirmed) {
        return;
    }

    await apiRequest(`/api/tickets/${ticketId}/`, {
        method: "DELETE"
    });

    await loadTickets();
}
