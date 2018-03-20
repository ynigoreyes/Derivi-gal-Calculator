// Home page and actual calculations
console.log('connected to JS');
var expr = document.getElementById('expr'),
    pretty = document.getElementById('pretty'),
    result = document.getElementById('result'),
    parenthesis = 'keep',
    implicit = 'hide';

// initialize with an example expression
expr.value = 'sin(90)';
// This will display an integral to the user using dx
pretty.innerHTML = '$$\\int(' + math.parse(expr.value).toTex({parenthesis: parenthesis}) + ') dx$$';

result.innerHTML = math.format(math.eval(expr.value));

expr.oninput = function () {
    var node = null;

    try {
        // parse the expression
        node = math.parse(expr.value);


        // evaluate the result of the expression
        // We will replace this code with
        result.innerHTML = math.format(node.compile().eval());
    } catch (err) {
        // insert the error message from the backend here
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