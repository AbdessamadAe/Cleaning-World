WORLD FunctionTest {
    SIZE(10, 10);
    ENTRY_DEF(1, 1, N);
    EXIT_DEF(10, 10, S);
}

FUNC add(X, Y) RETURNS INT {
    RETURN X + Y;
}

AGENT FunctionAgent {
    VAR result = 0;
    VAR x = 5;
    VAR y = 3;
    
    result = add(x, y);
    REPORT result;
}
