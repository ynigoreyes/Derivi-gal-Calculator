// Home page and actual calculations
console.log('connected to JS');
var expr = document.getElementById('expr'),
    pretty = document.getElementById('pretty'),
    result = document.getElementById('result'),
    solve = document.getElementById('solveButton'),
    expressionDropdown = document.getElementById('operationDropdown'),
    validPost = true,
    parenthesis = 'keep',
    implicit = 'hide';

// initialize with an example expression
expr.value = 'sin(x)';
// This will display an integral to the user using dx
pretty.innerHTML = '$$\\int(' + math.parse(expr.value).toTex({parenthesis: parenthesis}) + ') dx$$';
result.innerHTML = '<span style="color: green;"> Press Solve to Evaluate!</span>';

// result.innerHTML = math.format(math.eval(expr.value));

$(solve).on('click', function(){
    if(validPost == true){
        var postData = {
            "equation": expr.value,
            "operation": expressionDropdown.value

        }
        $.ajax({
            type: 'POST',
            url: '/api/evaluate',
            dataType: "json",
            contentType: 'application/json;charset=UTF-8',
            data: JSON.stringify(postData),
            success: function(responseData){
                console.log(responseData['data']['answer'])
                errorMessage = responseData['data']['errorMessage']
                if (errorMessage == null){
                    answer = responseData['data']['answer']
                    // result.innerHTML = math.format(node.compile().eval());
                    result.innerHTML = math.format(math.parse(answer));

                } else{
                    result.innerHTML = '<span style="color: red;">' + errorMessage + '</span>';
                }
            }
        });
    }
});


expr.oninput = function () {
    var node = null;

    try {
        // parse the expression
        node = math.parse(expr.value);


        // evaluate the result of the expression
        result.innerHTML = '<span style="color: green;"> Press Solve to Evaluate!</span>';
        validPost = true;
    } catch (err) {
        // insert the error message from the backend here
        validPost = false;
        result.innerHTML = '<span style="color: red;"> Cannot Read Input</span>';
    }

    try {
        // export the expression to LaTeX
        var latex = node ? '\\int(' + node.toTex({ parenthesis: parenthesis, implicit: implicit }) + ') dx' : '';

        // console.log('LaTeX expression:', latex);

        // display and re-render the expression
        var elem = MathJax.Hub.getAllJax('pretty')[0];
        MathJax.Hub.Queue(['Text', elem, latex]);

    } catch (err){ }
};
// Insert AJAX POST to backend for evaluation
// we want the backend to return an error message or the
// evaluated expression