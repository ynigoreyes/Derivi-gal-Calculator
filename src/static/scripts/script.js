// Home page and actual calculations
if (window.location.pathname == '/'){
    console.log('connected to JS');

    const initEquation = 'sqrt(75 / 3) + sin(x / 4)^2';

    var expr = document.getElementById('expr'),
        pretty = document.getElementById('pretty'),
        result = document.getElementById('result'),
        solve = document.getElementById('solveButton'),
        expressionDropdown = document.getElementById('operationDropdown'),
        operationState = 'integrate',
        errors = document.getElementById('errors'),
        equationPost = initEquation, // Equation we will be posting
        validPost = true,
        parenthesis = 'keep',
        implicit = 'hide';

    // initialize with an example expression
    expr.value = initEquation;
    pretty.innerHTML = '$$\\int' + math.parse(expr.value).toTex({ parenthesis: parenthesis }) + ' dx$$';

    // Event Listeners
    $(expressionDropdown).on('change', updateLatex);    // Listens for a  change in the operation choice
    $(expr).on('keyup', updateLatex);                 // Listens for keypresses on the equation text

    // Solves the equation by sending the information to backend for processing
    $(solve).on('click', function () {

        if (validPost == true) {
            var postData = {
                "equation": equationPost,
                "operation": expressionDropdown.value

            }
            // Sends a POST request to backend though AJAX
            // Uses the response to display the answer to the user
            $.ajax({
                type: 'POST',
                url: '/api/evaluate',
                contentType: 'application/json;charset=UTF-8',
                data: JSON.stringify(postData),
                success: function (responseData) {

                    errorMessage = responseData['data']['errorMessage']

                    if (errorMessage == null) {
                        answer = responseData['data']['answer']
                        if (expressionDropdown.value == 'integrate') {
                            result.innerHTML = "[" + math.format(math.parse(answer)) + "] + C";
                        } else if (expressionDropdown.value == 'derive') {
                            result.innerHTML = math.format(math.parse(answer))
                        };

                    } else {
                        result.innerHTML = '<span style="color: red;">' + errorMessage + '</span>';
                    }

                }
            });
        }
    });
    function updateLatex() {
        /*Shows what the user is typing*/
        var node = null;
        console.log('updating latex');
        operationState = expressionDropdown.value;
        console.log(operationState);
        try {
            // parse the expression
            node = math.parse(expr.value);
            // This is the part we send to the backend since it is the parsed equation
            equationPost = node.toString()
        }
        catch (err) { }

        try {
            // We check to see what kind of answer we display to the user
            if (operationState == 'integrate') {
                var latex = node ? "\\int" + node.toTex({ parenthesis: parenthesis }) + " dx" : '';
            } else if (operationState == 'derive') {
                var latex = node ? node.toTex({ parenthesis: parenthesis }) + " d/dx" : '';
            };
            // display and re-render the expression
            var elem = MathJax.Hub.getAllJax('pretty')[0];
            MathJax.Hub.Queue(['Text', elem, latex]);
        }
        catch (err) { }
    };
} else if(window.location.pathname == '/login'){
    console.log('Connected to login');
    const loginButton = document.getElementById('loginButton');
    const username = document.getElementById('usernameInput');
    const password = document.getElementById('passwordInput');

    $(u)
} else if(window.location.pathname == '/register'){
    console.log('Connected to register');
};

