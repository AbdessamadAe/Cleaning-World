WORLD TestLoops {
    SIZE(5, 5);
    ENTRY_DEF(1, 1, N);
    EXIT_DEF(5, 5, S);
}

AGENT LoopAgent {
    VAR counter = 0;
    VAR max = 3;
    
    WHILE counter LT max DO
        REPORT counter;
        counter = counter + 1;
    ENDWHILE;
    
    REPORT 99;
}
