// ======================================================
// ResolveAI — Frontend Logic
// Multi-Customer Persistent Memory
// ======================================================


// ======================================================
// HTML ELEMENTS
// ======================================================

const messageInput =
    document.getElementById("messageInput");

const sendBtn =
    document.getElementById("sendBtn");

const chatMessages =
    document.getElementById("chatMessages");

const connectionStatus =
    document.getElementById("connectionStatus");

const connectionText =
    document.getElementById("connectionText");

const interactionCount =
    document.getElementById("interactionCount");

const memoryCount =
    document.getElementById("memoryCount");

const startComplaintBtn =
    document.getElementById("startComplaintBtn");

const memoryBtn =
    document.getElementById("memoryBtn");

const customerNameElement =
    document.getElementById("customerName");

const customerIdElement =
    document.getElementById("customerId");

const customerAvatar =
    document.getElementById("customerAvatar");

const memoryCustomerName =
    document.getElementById("memoryCustomerName");

const memoryCustomerId =
    document.getElementById("memoryCustomerId");

const previousIssue =
    document.getElementById("previousIssue");

const previousAction =
    document.getElementById("previousAction");

const customerPreference =
    document.getElementById("customerPreference");

const switchCustomerBtn =
    document.getElementById("switchCustomerBtn");

const addCustomerBtn =
    document.getElementById("addCustomerBtn");

const learningInteractionText =
    document.getElementById("learningInteractionText");


// ======================================================
// CUSTOMER DATABASE
// ======================================================

let customers =
    JSON.parse(
        localStorage.getItem("resolveai_customers")
    ) || {

        "RA-2048": {

            name: "Jordan Davis",

            interactions: 3,

            memories: 3,

            messages: [],

            previousIssue:
                "Wireless headphones arrived damaged.",

            previousAction:
                "Replacement requested.",

            preference:
                "Customer prefers quick resolutions and may prefer a refund over another replacement."
        }
    };


// ======================================================
// CURRENT CUSTOMER
// ======================================================

let currentCustomerId =
    localStorage.getItem(
        "resolveai_current_customer"
    ) || "RA-2048";


// Make sure current customer exists

if (!customers[currentCustomerId]) {

    currentCustomerId =
        Object.keys(customers)[0];

}


// ======================================================
// SAVE CUSTOMER DATABASE
// ======================================================

function saveCustomers() {

    localStorage.setItem(
        "resolveai_customers",
        JSON.stringify(customers)
    );

}


// ======================================================
// GET CURRENT CUSTOMER
// ======================================================

function getCurrentCustomer() {

    return customers[currentCustomerId];

}


// ======================================================
// SAVE CURRENT CUSTOMER ID
// ======================================================

function saveCurrentCustomer() {

    localStorage.setItem(
        "resolveai_current_customer",
        currentCustomerId
    );

}


// ======================================================
// HTML ESCAPE
// ======================================================

function escapeHTML(text) {

    const div =
        document.createElement("div");

    div.textContent =
        text ?? "";

    return div.innerHTML;

}


// ======================================================
// UPDATE CUSTOMER PROFILE
// ======================================================

function updateCustomerProfile() {

    const customer =
        getCurrentCustomer();

    if (!customer) {
        return;
    }


    // Name

    customerNameElement.textContent =
        customer.name;


    // ID

    customerIdElement.textContent =
        currentCustomerId;


    // Avatar

    customerAvatar.textContent =
        getInitials(
            customer.name
        );


    // Interactions

    interactionCount.textContent =
        customer.interactions;


    // Memory count

    memoryCount.textContent =
        customer.memories;


    // Learning section

    learningInteractionText.textContent =
        `${customer.interactions} Interactions`;


    // Memory customer

    memoryCustomerName.textContent =
        customer.name;


    memoryCustomerId.textContent =
        currentCustomerId;


    // Previous issue

    previousIssue.textContent =
        customer.previousIssue ||
        "No previous issue recorded yet.";


    // Previous action

    previousAction.textContent =
        customer.previousAction ||
        "No previous action recorded yet.";


    // Preference

    customerPreference.textContent =
        customer.preference ||
        "No customer preference learned yet.";


    saveCurrentCustomer();

}


// ======================================================
// GET INITIALS
// ======================================================

function getInitials(name) {

    if (!name) {
        return "CU";
    }

    return name
        .trim()
        .split(/\s+/)
        .map(
            word =>
                word.charAt(0)
        )
        .join("")
        .substring(0, 2)
        .toUpperCase();

}


// ======================================================
// BACKEND CONNECTION
// ======================================================

async function checkBackend() {

    try {

        const response =
            await fetch(
                `${API_CONFIG.BASE_URL}${API_CONFIG.HEALTH_ENDPOINT}`,
                {
                    method: "GET"
                }
            );


        if (!response.ok) {

            throw new Error(
                `Backend returned ${response.status}`
            );

        }


        setBackendStatus(true);

    }

    catch (error) {

        console.error(
            "Backend connection error:",
            error
        );

        setBackendStatus(false);

    }

}


// ======================================================
// BACKEND STATUS
// ======================================================

function setBackendStatus(isOnline) {

    if (
        !connectionStatus ||
        !connectionText
    ) {

        return;

    }


    if (isOnline) {

        connectionText.textContent =
            "Backend Connected";

        connectionStatus.style.background =
            "rgba(34, 197, 94, 0.08)";

        connectionStatus.style.borderColor =
            "rgba(34, 197, 94, 0.2)";

        connectionStatus.style.color =
            "#86efac";

    }

    else {

        connectionText.textContent =
            "Backend Offline";

        connectionStatus.style.background =
            "rgba(239, 68, 68, 0.08)";

        connectionStatus.style.borderColor =
            "rgba(239, 68, 68, 0.2)";

        connectionStatus.style.color =
            "#fca5a5";

    }

}


// ======================================================
// ADD MESSAGE TO CHAT
// ======================================================

function addMessage(
    sender,
    message,
    saveMessage = true
) {

    const wrapper =
        document.createElement("div");

    wrapper.className =
        sender === "customer"
            ? "message customer-message"
            : "message ai-message";


    const avatar =
        document.createElement("div");

    avatar.className =
        sender === "customer"
            ? "message-avatar"
            : "message-avatar ai-avatar";


    avatar.textContent =
        sender === "customer"
            ? getInitials(
                getCurrentCustomer().name
            )
            : "✦";


    const content =
        document.createElement("div");

    content.className =
        "message-content";


    const meta =
        document.createElement("div");

    meta.className =
        "message-meta";


    const name =
        document.createElement("strong");

    name.textContent =
        sender === "customer"
            ? getCurrentCustomer().name
            : "ResolveAI";


    const time =
        document.createElement("span");

    time.textContent =
        sender === "customer"
            ? "Customer"
            : "AI Agent";


    meta.appendChild(name);
    meta.appendChild(time);


    const bubble =
        document.createElement("div");

    bubble.className =
        "message-bubble";


    bubble.textContent =
        message;


    content.appendChild(meta);
    content.appendChild(bubble);

    wrapper.appendChild(avatar);
    wrapper.appendChild(content);

    chatMessages.appendChild(wrapper);


    chatMessages.scrollTop =
        chatMessages.scrollHeight;


    // Save message only when requested

    if (saveMessage) {

        const customer =
            getCurrentCustomer();

        if (customer) {

            customer.messages.push({

                sender:
                    sender,

                message:
                    message

            });

            saveCustomers();

        }

    }


    return wrapper;

}


// ======================================================
// MEMORY NOTICE
// ======================================================

function addMemoryNotice(text) {

    const notice =
        document.createElement("div");

    notice.className =
        "memory-notice";


    notice.innerHTML = `

        <span class="memory-icon">
            🧠
        </span>

        <div>

            <strong>
                Memory updated
            </strong>

            <p>
                ${escapeHTML(text)}
            </p>

        </div>

    `;


    chatMessages.appendChild(notice);


    chatMessages.scrollTop =
        chatMessages.scrollHeight;

}


// ======================================================
// TYPING INDICATOR
// ======================================================

function showTyping() {

    const typing =
        document.createElement("div");

    typing.id =
        "typingIndicator";

    typing.className =
        "message ai-message";


    typing.innerHTML = `

        <div class="message-avatar ai-avatar">
            ✦
        </div>

        <div class="message-content">

            <div class="message-meta">

                <strong>
                    ResolveAI
                </strong>

                <span>
                    Thinking...
                </span>

            </div>

            <div class="message-bubble">

                🧠 Recalling customer memory...

            </div>

        </div>

    `;


    chatMessages.appendChild(typing);


    chatMessages.scrollTop =
        chatMessages.scrollHeight;

}


// ======================================================
// REMOVE TYPING
// ======================================================

function removeTyping() {

    const typing =
        document.getElementById(
            "typingIndicator"
        );

    if (typing) {

        typing.remove();

    }

}


// ======================================================
// SEND MESSAGE
// ======================================================

async function sendMessage() {

    const message =
        messageInput.value.trim();


    if (!message) {

        return;

    }


    const customer =
        getCurrentCustomer();


    if (!customer) {

        return;

    }


    // --------------------------------------------------
    // Show customer message temporarily
    // IMPORTANT:
    // Do NOT save it yet.
    // --------------------------------------------------

    const customerMessageElement =
        addMessage(
            "customer",
            message,
            false
        );


    // Clear input

    messageInput.value = "";


    // Show AI thinking

    showTyping();


    // Disable button

    sendBtn.disabled =
        true;

    sendBtn.style.opacity =
        "0.6";


    try {

        // --------------------------------------------------
        // SEND REQUEST TO BACKEND
        // --------------------------------------------------

        const response =
            await fetch(
                `${API_CONFIG.BASE_URL}${API_CONFIG.CHAT_ENDPOINT}`,
                {

                    method: "POST",

                    headers: {

                        "Content-Type":
                            "application/json"

                    },

                    body: JSON.stringify({

                        customer_id:
                            currentCustomerId,

                        message:
                            message

                    })

                }
            );


        // --------------------------------------------------
        // Read response safely
        // --------------------------------------------------

        let data = {};

        const contentType =
            response.headers.get(
                "content-type"
            ) || "";


        if (
            contentType.includes(
                "application/json"
            )
        ) {

            data =
                await response.json();

        }

        else {

            const text =
                await response.text();

            data = {
                detail:
                    text
            };

        }


        // --------------------------------------------------
        // Backend returned an error
        // --------------------------------------------------

        if (!response.ok) {

            throw new Error(

                data.detail ||
                data.error ||
                data.message ||
                `Server error: ${response.status}`

            );

        }


        // --------------------------------------------------
        // Backend successful
        // --------------------------------------------------

        removeTyping();


        const aiResponse =
            data.response ||
            data.reply ||
            data.message ||
            "I received your request.";


        // --------------------------------------------------
        // NOW save customer message
        // because backend succeeded
        // --------------------------------------------------

        customer.messages.push({

            sender:
                "customer",

            message:
                message

        });


        // --------------------------------------------------
        // Show AI response and save it
        // --------------------------------------------------

        addMessage(
            "ai",
            aiResponse,
            true
        );


        // Backend online

        setBackendStatus(true);


        // --------------------------------------------------
        // Update customer information
        // --------------------------------------------------

        try {

            updateCustomerAfterMessage(
                data,
                message
            );

        }

        catch (uiError) {

            // A frontend UI error should NOT
            // be treated as a backend failure.

            console.error(
                "Frontend update error:",
                uiError
            );

        }


        // Save successful interaction

        saveCustomers();

    }


    catch (error) {

        console.error(
            "Chat request error:",
            error
        );


        removeTyping();


        // Remove temporary customer message
        // because backend request failed.

        if (customerMessageElement) {

            customerMessageElement.remove();

        }


        // Restore typed message

        messageInput.value =
            message;


        // Do NOT automatically say backend is offline
        // unless the actual error is a network error.

        const errorMessage =
            error &&
            error.message
                ? error.message
                : "Unknown error";


        let displayError =
            "Something went wrong while processing your request.";


        // Network / connection error

        if (
            error instanceof TypeError ||
            errorMessage
                .toLowerCase()
                .includes("failed to fetch")
        ) {

            setBackendStatus(false);

            displayError =
                "I couldn't reach the ResolveAI backend. Please check that the backend laptop and API server are running.";

        }

        else {

            // Backend responded but returned an error

            setBackendStatus(true);

            displayError =
                `ResolveAI could not process this request: ${errorMessage}`;

        }


        addMessage(
            "ai",
            displayError,
            false
        );

    }


    finally {

        sendBtn.disabled =
            false;

        sendBtn.style.opacity =
            "1";

    }

}


// ======================================================
// UPDATE CUSTOMER AFTER MESSAGE
// ======================================================

function updateCustomerAfterMessage(
    data,
    userMessage
) {

    const customer =
        getCurrentCustomer();


    if (!customer) {

        return;

    }


    // Increase interaction count

    customer.interactions++;


    // Hindsight memory count

    if (
        data.memory_count !==
            undefined &&
        data.memory_count !==
            null
    ) {

        customer.memories =
            Number(
                data.memory_count
            );

    }

    else {

        customer.memories++;

    }


    // Learn simple context from message

    const lowerMessage =
        userMessage.toLowerCase();


    // Damaged / broken issue

    if (
        lowerMessage.includes(
            "damaged"
        ) ||
        lowerMessage.includes(
            "broken"
        )
    ) {

        customer.previousIssue =
            userMessage;

    }


    // Replacement

    if (
        lowerMessage.includes(
            "replacement"
        )
    ) {

        customer.previousAction =
            "Replacement requested.";

    }


    // Refund

    if (
        lowerMessage.includes(
            "refund"
        )
    ) {

        customer.preference =
            "Customer prefers a refund instead of another replacement.";

    }


    // Replace

    if (
        lowerMessage.includes(
            "replace"
        )
    ) {

        customer.preference =
            "Customer is considering a replacement.";

    }


    saveCustomers();


    updateCustomerProfile();


    let memoryText =
        "Hindsight recalled and updated customer context.";


    if (
        data.saved === true
    ) {

        memoryText =
            "Hindsight recalled previous context and saved this interaction.";

    }


    addMemoryNotice(
        memoryText
    );

}


// ======================================================
// LOAD CUSTOMER CHAT
// ======================================================

function loadCustomerChat() {

    // Clear existing chat

    chatMessages.innerHTML = "";


    const customer =
        getCurrentCustomer();


    if (!customer) {

        return;

    }


    // Update profile

    updateCustomerProfile();


    // Existing customer history

    if (
        customer.messages &&
        customer.messages.length > 0
    ) {

        customer.messages.forEach(
            item => {

                addMessage(
                    item.sender,
                    item.message,
                    false
                );

            }
        );

    }


    else {

        // New customer

        addMessage(
            "customer",
            `Hello, I am ${customer.name}. I need help with my issue.`,
            false
        );


        addMessage(
            "ai",
            `Hello ${customer.name}. I'm ResolveAI. Please describe your complaint and I'll remember the important details for your future interactions.`,
            false
        );

    }


    chatMessages.scrollTop =
        chatMessages.scrollHeight;

}


// ======================================================
// ADD NEW CUSTOMER
// ======================================================

function addCustomer() {

    const name =
        prompt(
            "Enter new customer name:"
        );


    if (
        !name ||
        !name.trim()
    ) {

        return;

    }


    const id =
        prompt(
            "Enter unique Customer ID:\nExample: RA-2049"
        );


    if (
        !id ||
        !id.trim()
    ) {

        return;

    }


    const cleanName =
        name.trim();


    const cleanId =
        id.trim().toUpperCase();


    // Check duplicate ID

    if (
        customers[cleanId]
    ) {

        alert(
            "This Customer ID already exists. Please use a different ID."
        );

        return;

    }


    // Create customer

    customers[cleanId] = {

        name:
            cleanName,

        interactions:
            0,

        memories:
            0,

        messages:
            [],

        previousIssue:
            "No previous issue recorded yet.",

        previousAction:
            "No previous action recorded yet.",

        preference:
            "No customer preference learned yet."

    };


    // Make new customer active

    currentCustomerId =
        cleanId;


    saveCustomers();

    saveCurrentCustomer();


    // Load new customer

    loadCustomerChat();


    alert(
        `${cleanName} has been added successfully.`
    );

}


// ======================================================
// SWITCH CUSTOMER
// ======================================================

function switchCustomer() {

    const ids =
        Object.keys(customers);


    if (
        ids.length <= 1
    ) {

        alert(
            "You currently have only one customer. Click '+ Add Customer' to create another customer."
        );

        return;

    }


    const customerList =
        ids
            .map(
                (id, index) =>
                    `${index + 1}. ${customers[id].name} (${id})`
            )
            .join("\n");


    const choice =
        prompt(
            "SELECT CUSTOMER\n\n" +
            customerList +
            "\n\nEnter customer number:"
        );


    if (!choice) {

        return;

    }


    const selectedIndex =
        Number(choice) - 1;


    if (
        isNaN(selectedIndex) ||
        selectedIndex < 0 ||
        selectedIndex >= ids.length
    ) {

        alert(
            "Invalid customer selection."
        );

        return;

    }


    // Change active customer

    currentCustomerId =
        ids[selectedIndex];


    saveCurrentCustomer();


    // Load selected customer's
    // own chat and profile

    loadCustomerChat();

}


// ======================================================
// EDIT CUSTOMER
// ======================================================

// Double-click customer name
// to change name and ID

function editCurrentCustomer() {

    const customer =
        getCurrentCustomer();


    if (!customer) {

        return;

    }


    const newName =
        prompt(
            "Change customer name:",
            customer.name
        );


    if (
        newName &&
        newName.trim()
    ) {

        customer.name =
            newName.trim();

    }


    const newId =
        prompt(
            "Change Customer ID:",
            currentCustomerId
        );


    if (
        newId &&
        newId.trim()
    ) {

        const updatedId =
            newId.trim().toUpperCase();


        if (
            updatedId !==
            currentCustomerId
        ) {

            if (
                customers[updatedId]
            ) {

                alert(
                    "That Customer ID already exists."
                );

                return;

            }


            // Move customer to new ID

            customers[updatedId] =
                customer;


            delete customers[
                currentCustomerId
            ];


            currentCustomerId =
                updatedId;

        }

    }


    saveCustomers();

    saveCurrentCustomer();

    loadCustomerChat();

}


// ======================================================
// CUSTOMER BUTTONS
// ======================================================

if (switchCustomerBtn) {

    switchCustomerBtn.addEventListener(
        "click",
        switchCustomer
    );

}


if (addCustomerBtn) {

    addCustomerBtn.addEventListener(
        "click",
        addCustomer
    );

}


// Double click current customer name

if (customerNameElement) {

    customerNameElement.addEventListener(
        "dblclick",
        editCurrentCustomer
    );


    customerNameElement.style.cursor =
        "pointer";


    customerNameElement.title =
        "Double-click to edit customer name and ID";

}


// ======================================================
// ENTER KEY
// ======================================================

messageInput.addEventListener(
    "keydown",
    function(event) {

        if (
            event.key === "Enter" &&
            !event.shiftKey
        ) {

            event.preventDefault();

            sendMessage();

        }

    }
);


// ======================================================
// SEND BUTTON
// ======================================================

sendBtn.addEventListener(
    "click",
    sendMessage
);


// ======================================================
// RESOLVE COMPLAINT BUTTON
// ======================================================

startComplaintBtn.addEventListener(
    "click",
    function() {

        document
            .getElementById("conversation")
            .scrollIntoView({
                behavior:
                    "smooth"
            });


        setTimeout(
            () =>
                messageInput.focus(),
            500
        );

    }
);


// ======================================================
// EXPLORE MEMORY BUTTON
// ======================================================

memoryBtn.addEventListener(
    "click",
    function() {

        document
            .getElementById("memory")
            .scrollIntoView({
                behavior:
                    "smooth"
            });

    }
);


// ======================================================
// START APPLICATION
// ======================================================

saveCustomers();

saveCurrentCustomer();

loadCustomerChat();

checkBackend();


// Check backend every 10 seconds

setInterval(
    checkBackend,
    10000
);