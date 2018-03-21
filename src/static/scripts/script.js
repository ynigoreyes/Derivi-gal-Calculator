// Home page and actual calculations
console.log('connected to JS');
var expr = document.getElementById('expr'),
    pretty = document.getElementById('pretty'),
    result = document.getElementById('result'),
    solve = document.getElementById('solveButton'),
    expressionDropdown = document.getElementById('operationDropdown'),
    operationState = 'integrate',
    errors = document.getElementById('errors'),
    equationPost = 'sqrt(75 / 3) + sin(pi / 4)^2', // Equation we will be posting
    validPost = true,
    parenthesis = 'keep',
    implicit = 'hide';

// initialize with an example expression
expr.value = 'sqrt(75 / 3) + sin(pi / 4)^2';
pretty.innerHTML = '$$\\int' + math.parse(expr.value).toTex({ parenthesis: parenthesis }) + ' dx$$';

$(expressionDropdown).on('change', function(){
    console.log('change operations')
    operationState = $(this).val();
    console.log(operationState);
    if (operationState == 'integrate') {
        console.log('using integrate');
        updateLatex()
    } else if (operationState == 'derive') {
        console.log('using derive');
        updateLatex()
    };
});

// Solves the equation by sending the information to backend for processing
$(solve).on('click', function(){
    console.log('solving...')
    console.log('sending ' + equationPost + ' to evaluate...')
    if(validPost == true){
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
            success: function(responseData){

                errorMessage = responseData['data']['errorMessage']
                if (errorMessage == null){
                    answer = responseData['data']['answer']
                    console.log(answer)
                    result.innerHTML = "[" + math.format(math.parse(answer)) + "] + C";

                } else{
                    result.innerHTML = '<span style="color: red;">' + errorMessage + '</span>';
                }

            }
        });
    }
});

expr.oninput = updateLatex;

function updateLatex() {
    var node = null;
    try {
        // parse the expression // Interupt the original chain
        node = math.parse(expr.value);
        equationPost = node.toString()
    }
    catch (err) {}

    try {
        if (operationState == 'integrate'){
            var latex = node ? "\\int" + node.toTex({ parenthesis: parenthesis }) + " dx" : '';
            console.log('LaTeX expression:', latex);
        } else if (operationState == 'derive'){
            var latex = node ? node.toTex({ parenthesis: parenthesis }) + " d/dx" : '';
            console.log('LaTeX expression:', latex);
        };
        // export the expression to LaTeX

        // display and re-render the expression
        var elem = MathJax.Hub.getAllJax('pretty')[0];
        MathJax.Hub.Queue(['Text', elem, latex]);
    }
    catch (err) { }
};
