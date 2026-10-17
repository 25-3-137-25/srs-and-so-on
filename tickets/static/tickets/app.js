const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;
const categorySelect = document.getElementById("category");
const form = document.getElementById("ticket-form");
const titleInput = document.getElementById("title");
const descriptionInput = document.getElementById("description");
const createButton = document.getElementById("create-ticket");
const message = document.getElementById("message");
const list = document.getElementById("tickets-list");
const loading = document.getElementById("loading");
const filter = document.getElementById("status-filter");
const refreshButton = document.getElementById("refresh-tickets");
let latestLoad = 0;

function errorText(data) {
    if (Array.isArray(data)) return data.map(errorText).join(" ");
    if (data && typeof data === "object") {
        const labels = { title: "Название", category: "Категория", status: "Статус", description: "Описание" };
        return Object.entries(data).map(([key, value]) =>
            `${labels[key] ? labels[key] + ": " : ""}${errorText(value)}`
        ).join(" ");
    }
    return String(data ?? "Ошибка выполнения запроса");
}

async function apiRequest(url, options = {}) {
    let response;
    try {
        response = await fetch(url, {
            ...options,
            headers: {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken,
                ...(options.headers || {})
            },
            credentials: "same-origin"
        });
    } catch {
        throw new Error("Нет связи с сервером. Проверьте подключение и обновите список перед повторной попыткой.");
    }

    if (response.status === 204) return null;
    const data = await response.json().catch(() => null);
    if (!response.ok) {
        if (response.status === 401 || response.status === 403) {
            throw new Error("Нет доступа. Войдите в систему или обновите страницу и повторите попытку.");
        }
        if (response.status === 404) {
            throw new Error("Заявка не найдена. Обновите список.");
        }
        throw new Error(data ? errorText(data) : `Ошибка сервера (${response.status}).`);
    }
    if (data === null) throw new Error("Сервер вернул некорректный ответ. Обновите список.");
    return data;
}

function showMessage(text, isError = false) {
    message.textContent = text;
    message.className = "alert " + (isError ? "alert-danger" : "alert-success");
    message.setAttribute("role", isError ? "alert" : "status");
}

async function loadCategories() {
    const categories = await apiRequest("/api/categories/");
    categorySelect.replaceChildren();
    for (const category of categories) {
        const option = document.createElement("option");
        option.value = category.id;
        option.textContent = category.name;
        categorySelect.append(option);
    }
    createButton.disabled = categories.length === 0;
    if (!categories.length) {
        showMessage("Нет категорий. Добавьте категорию в панели администратора, затем обновите страницу.", true);
    }
}

function renderTicket(ticket) {
    const row = document.createElement("div");
    row.className = "d-flex flex-wrap justify-content-between align-items-center border-bottom py-3 gap-3";
    const details = document.createElement("div");
    const title = document.createElement("div");
    title.className = "fw-bold text-break";
    title.textContent = ticket.title;
    const category = document.createElement("div");
    category.className = "text-secondary text-break";
    category.textContent = ticket.category_name;
    const description = document.createElement("div");
    description.className = "text-break";
    description.textContent = ticket.description;
    details.append(title, category, description);

    const status = document.createElement("span");
    status.className = "badge bg-blue-lt";
    status.textContent = ticket.status_label;

    const actions = document.createElement("fieldset");
    actions.className = "d-flex flex-wrap align-items-center gap-2 border-0 m-0 p-0";
    actions.setAttribute("aria-label", `Действия с заявкой «${ticket.title}»`);
    const statusForm = document.createElement("form");
    statusForm.className = "d-flex flex-wrap gap-2";
    const select = document.createElement("select");
    select.className = "form-select w-auto";
    select.setAttribute("aria-label", `Новый статус заявки «${ticket.title}»`);
    for (const nextStatus of ticket.allowed_statuses) {
        const option = document.createElement("option");
        option.value = nextStatus.value;
        option.textContent = nextStatus.label;
        select.append(option);
    }
    const statusButton = document.createElement("button");
    statusButton.type = "submit";
    statusButton.className = "btn btn-outline-primary";
    statusButton.textContent = "Изменить статус";
    if (!ticket.allowed_statuses.length) {
        const option = document.createElement("option");
        option.textContent = "Нет переходов";
        select.append(option);
        select.disabled = true;
        statusButton.disabled = true;
        statusButton.title = "Заявка выполнена. Дальнейшая смена статуса недоступна.";
    }
    statusForm.append(select, statusButton);
    statusForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        if (actions.disabled || !select.value || statusButton.disabled) return;
        await runOperation(actions, () => changeStatus(ticket.id, select.value),
            "Статус заявки изменён.", "Не удалось изменить статус: ");
    });

    const deleteButton = document.createElement("button");
    deleteButton.type = "button";
    deleteButton.className = "btn btn-outline-danger";
    deleteButton.textContent = "Удалить";
    deleteButton.addEventListener("click", async () => {
        if (actions.disabled) return;
        await runOperation(actions, () => deleteTicket(ticket.id, ticket.title),
            "Заявка удалена.", "Не удалось удалить заявку: ");
    });
    actions.append(statusForm, deleteButton);
    row.append(details, status, actions);
    return row;
}

async function loadTickets() {
    const loadId = ++latestLoad;
    loading.hidden = false;
    list.setAttribute("aria-busy", "true");
    const params = new URLSearchParams();
    if (filter.value) params.set("status", filter.value);
    const query = params.toString();
    try {
        const tickets = await apiRequest("/api/tickets/" + (query ? "?" + query : ""));
        // Ignore an older response if the user has already changed the filter.
        if (loadId !== latestLoad) return;
        list.replaceChildren();
        if (!tickets.length) {
            const empty = document.createElement("p");
            empty.textContent = "Заявки не найдены";
            list.append(empty);
        } else {
            for (const ticket of tickets) list.append(renderTicket(ticket));
        }
    } catch (error) {
        if (loadId === latestLoad) throw error;
    } finally {
        if (loadId === latestLoad) {
            loading.hidden = true;
            list.setAttribute("aria-busy", "false");
        }
    }
}

async function changeStatus(ticketId, newStatus) {
    await apiRequest(`/api/tickets/${ticketId}/`, {
        method: "PATCH",
        body: JSON.stringify({ status: newStatus })
    });
    return true;
}

async function deleteTicket(ticketId, ticketTitle) {
    if (!window.confirm(`Удалить заявку «${ticketTitle}»? Это действие нельзя отменить.`)) return false;
    await apiRequest(`/api/tickets/${ticketId}/`, { method: "DELETE" });
    return true;
}

async function runOperation(controls, operation, successMessage, errorPrefix) {
    controls.disabled = true;
    try {
        if (await operation() === false) return;
        showMessage(successMessage);
        try {
            await loadTickets();
        } catch (error) {
            showMessage(`${successMessage} Не удалось обновить список: ${error.message}`, true);
        }
    } catch (error) {
        showMessage(errorPrefix + error.message, true);
    } finally {
        controls.disabled = false;
    }
}

form.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (createButton.disabled) return;
    const payload = {
        title: titleInput.value.trim(),
        description: descriptionInput.value,
        category: Number(categorySelect.value)
    };
    await runOperation(createButton, async () => {
        await apiRequest("/api/tickets/", { method: "POST", body: JSON.stringify(payload) });
        // Preserve any new text typed while the request was in progress.
        if (titleInput.value.trim() === payload.title) titleInput.value = "";
        if (descriptionInput.value === payload.description) descriptionInput.value = "";
    }, "Заявка успешно создана.", "Не удалось создать заявку: ");
});

async function refreshTickets() {
    try {
        await loadTickets();
    } catch (error) {
        showMessage("Не удалось загрузить заявки: " + error.message, true);
    }
}

filter.addEventListener("change", refreshTickets);
refreshButton.addEventListener("click", refreshTickets);

async function initialize() {
    await Promise.all([
        loadCategories().catch((error) => showMessage("Не удалось загрузить категории: " + error.message, true)),
        refreshTickets()
    ]);
}

initialize();
