const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;

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
        const errors = data || { detail: "Ошибка выполнения запроса" };
        throw new Error(JSON.stringify(errors));
    }
    return data;
}

const facultySelect = document.getElementById("faculty");
const form = document.getElementById("group-form");
const nameInput = document.getElementById("name");
const studentsInput = document.getElementById("students_count");
const messageBox = document.getElementById("message");
const list = document.getElementById("groups-list");
const loading = document.getElementById("loading");
const filter = document.getElementById("status-filter");

function showMessage(text, isError = false) {
    messageBox.textContent = text;
    messageBox.className = "alert " + (isError ? "alert-danger" : "alert-success");
    setTimeout(() => { messageBox.textContent = ""; messageBox.className = ""; }, 4000);
}

function parseError(error) {
    try {
        const obj = JSON.parse(error.message);
        const messages = [];
        for (const key in obj) {
            const val = obj[key];
            if (Array.isArray(val)) messages.push(`${key}: ${val.join(", ")}`);
            else messages.push(`${key}: ${val}`);
        }
        return messages.join("; ");
    } catch (e) {
        return error.message;
    }
}

async function loadFaculties() {
    const faculties = await apiRequest("/crud-groups/api/faculties/");
    facultySelect.replaceChildren();
    for (const f of faculties) {
        const opt = document.createElement("option");
        opt.value = f.id;
        opt.textContent = `${f.code} — ${f.name}`;
        facultySelect.append(opt);
    }
}

async function loadGroups() {
    loading.hidden = false;
    const params = new URLSearchParams();
    if (filter.value) params.set("status", filter.value);
    const query = params.toString();
    const url = "/crud-groups/api/groups/" + (query ? "?" + query : "");

    try {
        const groups = await apiRequest(url);
        list.replaceChildren();

        if (groups.length === 0) {
            const empty = document.createElement("p");
            empty.className = "text-muted";
            empty.textContent = "Группы не найдены";
            list.append(empty);
            return;
        }

        for (const g of groups) {
            const row = document.createElement("div");
            row.className = "d-flex justify-content-between align-items-center border-bottom py-3 gap-3";

            const info = document.createElement("div");
            info.innerHTML = `
                <div><strong>${g.name}</strong> — ${g.faculty_name}</div>
                <div class="text-muted small">Студентов: ${g.students_count} | Куратор: ${g.curator_name || "—"}</div>
            `;

            const statusClass = {
                recruiting: "status-recruiting",
                studying: "status-studying",
                graduated: "status-graduated"
            }[g.status];

            const status = document.createElement("span");
            status.className = `status-badge ${statusClass}`;
            status.textContent = {
                recruiting: "Набор открыт",
                studying: "Обучение",
                graduated: "Выпущена"
            }[g.status];

            const actions = document.createElement("div");
            actions.className = "d-flex gap-2";

            const nextStatus = {
                recruiting: { value: "studying", label: "→ Обучение" },
                studying: { value: "graduated", label: "→ Выпустить" },
                graduated: null
            }[g.status];

            if (nextStatus) {
                const btnStatus = document.createElement("button");
                btnStatus.className = "btn btn-sm btn-outline-primary";
                btnStatus.textContent = nextStatus.label;
                btnStatus.onclick = () => changeStatus(g.id, nextStatus.value);
                actions.append(btnStatus);
            }

            const btnDelete = document.createElement("button");
            btnDelete.className = "btn btn-sm btn-outline-danger";
            btnDelete.textContent = "Удалить";
            btnDelete.onclick = () => deleteGroup(g.id, g.name);
            actions.append(btnDelete);

            row.append(info, status, actions);
            list.append(row);
        }
    } catch (error) {
        showMessage("Не удалось загрузить группы: " + parseError(error), true);
    } finally {
        loading.hidden = true;
    }
}

form.addEventListener("submit", async (event) => {
    event.preventDefault();
    try {
        await apiRequest("/crud-groups/api/groups/", {
            method: "POST",
            body: JSON.stringify({
                name: nameInput.value,
                faculty: Number(facultySelect.value),
                students_count: Number(studentsInput.value) || 0
            })
        });
        nameInput.value = "";
        studentsInput.value = 0;
        showMessage("Группа успешно создана");
        await loadGroups();
    } catch (error) {
        showMessage("Ошибка: " + parseError(error), true);
    }
});

async function changeStatus(groupId, newStatus) {
    try {
        await apiRequest(`/crud-groups/api/groups/${groupId}/`, {
            method: "PATCH",
            body: JSON.stringify({ status: newStatus })
        });
        showMessage("Статус обновлён");
        await loadGroups();
    } catch (error) {
        showMessage("Ошибка: " + parseError(error), true);
    }
}

async function deleteGroup(groupId, groupName) {
    if (!confirm(`Удалить группу «${groupName}»?`)) return;
    try {
        await apiRequest(`/crud-groups/api/groups/${groupId}/`, { method: "DELETE" });
        showMessage("Группа удалена");
        await loadGroups();
    } catch (error) {
        showMessage("Ошибка удаления: " + parseError(error), true);
    }
}

filter.addEventListener("change", loadGroups);

async function initialize() {
    try {
        await loadFaculties();
        await loadGroups();
    } catch (error) {
        showMessage("Ошибка инициализации: " + parseError(error), true);
    }
}
initialize();