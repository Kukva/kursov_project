document.addEventListener('DOMContentLoaded', () => {
    const registerContainer = document.getElementById('registerContainer');
    const loginContainer = document.getElementById('loginContainer');
    const dashboardContainer = document.getElementById('dashboardContainer');
    const historyContainer = document.getElementById('history');

    document.getElementById('showLogin').addEventListener('click', () => {
        registerContainer.classList.add('hidden');
        loginContainer.classList.remove('hidden');
    });

    document.getElementById('showRegister').addEventListener('click', () => {
        loginContainer.classList.add('hidden');
        registerContainer.classList.remove('hidden');
    });

    document.getElementById('registerForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('regUsername').value;
        const password = document.getElementById('regPassword').value;
        const email = document.getElementById('regEmail').value;
        const user_type = document.getElementById('userType').value;

        const data = { username, password, email, user_type};

        const queryString = new URLSearchParams(data).toString();
        // Определяем URL запроса
        const requestUrl = `/user/signup?${queryString}`;

        try {
            const response = await fetch(requestUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
    
            // Проверяем, что ответ успешный
            if (response.ok) {
                const responseData = await response.json();
                console.log('Response Data:', responseData);
    
                // Выполняем действия только при успешном ответе
                registerContainer.classList.add('hidden');
                loginContainer.classList.remove('hidden');
            } else {
                // Обработка ошибок, если ответ не успешный
                const errorData = await response.json();
                console.error('Error Response Data:', errorData);
                alert('Login failed: ' + (errorData.message || 'Unknown error'));
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred: ' + error.message);
        }


    });

    document.getElementById('loginForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('loginEmail').value;
        const password = document.getElementById('loginPassword').value;

        const data = {email, password};

        const queryString = new URLSearchParams(data).toString();
        // Определяем URL запроса
        const requestUrl = `/user/signin?${queryString}`;

        try {
            const response = await fetch(requestUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
    
            // Проверяем, что ответ успешный
            if (response.ok) {
                const responseData = await response.json();
                console.log('Response Data:', responseData);
                
                sessionStorage.setItem('userId', responseData.user_id);
                sessionStorage.setItem('userType', responseData.user_type);
                // Выполняем действия только при успешном ответе
                loginContainer.classList.add('hidden');
                dashboardContainer.classList.remove('hidden');
                // fetchHistory();
                // startFetchingHistory();
                // TransactionHistory();
                // startFetchingTrans()
                toggleTabs();
                console.log(responseData)
            } else {
                // Обработка ошибок, если ответ не успешный
                const errorData = await response.json();
                console.error('Error Response Data:', errorData);
                alert('Login failed: ' + (errorData.message || 'Unknown error'));
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred: ' + error.message);
        }
    });

    document.getElementById('requestForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const userId = sessionStorage.getItem('userId');;

        const project_name = document.getElementById('project_name').value;
        const category = document.getElementById('category').value;
        const created_date = document.getElementById('created_date').value;
        const launch_date = document.getElementById('launch_date').value;
        const deadline_date = document.getElementById('deadline_date').value;
        const goal_amount = parseFloat(document.getElementById('goal_amount').value);
        const staff_pick = document.getElementById('staff_pick').checked ? 1 : 0; // Assuming it's a checkbox
        const num_projects_created = parseInt(document.getElementById('num_projects_created').value);
        const num_projects_backed = parseInt(document.getElementById('num_projects_backed').value);
        const project_description = document.getElementById('project_description').value;
        const creator_description = document.getElementById('creator_description').value;
        
        const data = {
            project_name,
            category,
            created_date,
            launch_date,
            deadline_date,
            goal_amount,
            staff_pick,
            num_projects_created,
            num_projects_backed,
            project_description,
            creator_description
        };
        const queryString = new URLSearchParams(data).toString();
        console.log('query', queryString)
        
        try {
            console.log('Отправлен запрос в ml')
            const response = await fetch(`/ml/process_request/${userId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            console.log('Fetch completed');
            const result = await response.json();
            if (response.ok) {
                alert(`Prediction: ${result.prediction_name}`);
                // fetchHistory();
                document.getElementById('result-content').innerHTML = ` `
                document.getElementById('result-content').innerHTML = `
                    <p><strong>Prediction:</strong> ${result.prediction === 1 ? "Successful" : "Unsuccessful"}</p>
                    <p><strong>Recommendation:</strong> ${result.recommendations}</p>
                `
                // const mlResultTab = new bootstrap.Tab(document.getElementById('result-tab'));
                // mlResultTab.show();
            } else {
                alert(result.message);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to process request. Please try again.');
        }
    });

    async function fetchHistory() {
        const userId = sessionStorage.getItem('userId');
        const requestURL = `/ml/prediction_history/${userId}`;
    
        try {
            const response = await fetch(requestURL);
            const history = await response.json();
            const historyContainer = document.getElementById('history');
            historyContainer.innerHTML = ''; // Очищаем предыдущую историю
    
            history.forEach(item => {
                const div = document.createElement('div');
                const text =  `Project name: ${item.project_name}; Prediction: ${item.prediction}; Successful rate: ${item.pred_rate}; Time: ${item.timestamp}`
                div.innerText = text;
                historyContainer.appendChild(div);
            });
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to fetch history. Please try again.');
        }
    }
    
    function startFetchingHistory(interval = 5000) {
        fetchHistory(); // Первоначальный вызов
        setInterval(fetchHistory, interval);
    }


    function toggleTabs() {
        const mlTab = document.getElementById('ml-tab');
        // const trTab = document.getElementById('transaction-tab')
        const infoTab = document.getElementById('info-tab')
        const resultTab = document.getElementById('result-tab')
        // const historyTab = document.getElementById('history-tab')
        const predictionHistoryTab = document.createElement('li');
        predictionHistoryTab.className = 'nav-item';
        predictionHistoryTab.innerHTML = '<a class="nav-link" id="prediction-history-tab" data-toggle="tab" href="#predictionHistoryContent" role="tab" aria-controls="predictionHistoryContent" aria-selected="false">Prediction History</a>';
        user_type = sessionStorage.getItem('userType')
        if (user_type == 'startup') {
            // Агенты пока что видят тоже что и обычные юзеры
            // balanceTab.style.display = 'block';
            mlTab.style.display = 'block';
            infoTab.style.display = 'block';
            resultTab.style.display = 'block';
            // Можете добавить здесь аналогичный код для 'Transaction History'
        } else {
            // Обычный пользователь видит вкладки 'ML Request' и 'Profile'
            // balanceTab.style.display = 'none';
            mlTab.style.display = 'block';
            infoTab.style.display = 'block';
            resultTab.style.display = 'block';
            // Можете добавить здесь вкладку 'Profile', если она требуется
        }
    }

});