WORLD TestConditionals {
    SIZE(5, 5);
    ENTRY_DEF(1, 1, N);
    EXIT_DEF(5, 5, S);
}

AGENT ConditionalAgent {
    VAR x = 5;
    VAR y = 3;
    
    IF x GT y THEN
        REPORT 1;
    ELSE
        REPORT 0;
    ENDIF;
    
    IF x EQ 5 AND y LT 5 THEN
        REPORT 2;
    ELSE
        REPORT 3;
    ENDIF;
    
    IF x NEQ y OR y EQ 3 THEN
        REPORT 4;
    ELSE
        REPORT 5;
    ENDIF;
}
