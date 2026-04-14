from flask import Flask, request, jsonify, render_template
import ast
import operator
import math

app = Flask(__name__)

# operations
ops={
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: lambda a, b: a / b if b != 0 else "Error",
    ast.USub: operator.neg
}

def safe_eval(expr):
    def eval_node(node):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float, complex)):
            return node.value
        elif isinstance(node, ast.BinOp):
            op = ops.get(type(node.op))
            if not op:
                raise ValueError("Unsupported Operation")
            return op(eval_node(node.left), eval_node(node.right))
        elif isinstance(node, ast.UnaryOp):
            return ops[type(node.op)](eval_node(node.operand))
        else:
            raise ValueError("Invalid Expression")
    tree = ast.parse(expr, mode='eval')
    return eval_node(tree.body)

@app.route("/")
def index():
    return render_template("index.html")

@app.post("/calculate")
def calculate():
    data = request.get_json()
    expr = data.get("expression", "")

    try:
        result = safe_eval(expr)
        return jsonify({"result": result})
    except Exception:
        return jsonify({"error": "Invalid expression"}), 400

if __name__ == "__main__":
    app.run(debug=True)