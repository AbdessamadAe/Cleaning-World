WORLD TestFunctions {
    SIZE(5, 5);
    ENTRY_DEF(1, 1, N);
    EXIT_DEF(5, 5, S);
}

FUNC add(A, B) RETURNS INT {
    RETURN A + B;
}

AGENT FunctionAgent {
    VAR result1 = 0;
    VAR result2 = 0;
    
    result1 = add(2, 3);
    REPORT result1;
    
    result2 = add(10, 5);
    REPORT result2;
    
    REPORT add(result1, result2);
}
