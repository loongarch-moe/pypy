static void *slp_switch(void *(*save_state)(void *, void *),
                        void *(*restore_state)(void *, void *),
                        void *extra) __attribute__((noinline, optimize("O1")));
static void *slp_switch(void *(*save_state)(void *, void *),
                        void *(*restore_state)(void *, void *),
                        void *extra) {
    void *result;
    __asm__ volatile(
            "addi.d $sp, $sp, -320\n"
            "st.d $s0, $sp, 16\n"
            "st.d $s1, $sp, 24\n"
            "st.d $s2, $sp, 32\n"
            "st.d $s3, $sp, 40\n"
            "st.d $s4, $sp, 48\n"
            "st.d $s5, $sp, 56\n"
            "st.d $s6, $sp, 64\n"
            "st.d $s7, $sp, 72\n"
            "st.d $s8, $sp, 80\n"
            "fst.d $fs0, $sp, 96\n"
            "fst.d $fs1, $sp, 104\n"
            "fst.d $fs2, $sp, 112\n"
            "fst.d $fs3, $sp, 120\n"
            "fst.d $fs4, $sp, 128\n"
            "fst.d $fs5, $sp, 136\n"
            "fst.d $fs6, $sp, 144\n"
            "fst.d $fs7, $sp, 152\n"
            "move $s0, %[restore_state]\n"
            "move $s1, %[extra]\n"
            "move $s2, $ra\n"
            "move $a0, $sp\n"
            "move $a1, $s1\n"
            "jirl $ra, %[save_state], 0\n"
            "beqz $a0, end\n"
            "move $a1, $s1\n"
            "move $sp, $a0\n"
            "jirl $ra, $s0, 0\n"
            "end:\n"
            "move %[result], $a0\n"
            "ld.d $s0, $sp, 16\n"
            "ld.d $s1, $sp, 24\n"
            "ld.d $s2, $sp, 32\n"
            "ld.d $s3, $sp, 40\n"
            "ld.d $s4, $sp, 48\n"
            "ld.d $s5, $sp, 56\n"
            "ld.d $s6, $sp, 64\n"
            "ld.d $s7, $sp, 72\n"
            "ld.d $s8, $sp, 80\n"
            "fld.d $fs0, $sp, 96\n"
            "fld.d $fs1, $sp, 104\n"
            "fld.d $fs2, $sp, 112\n"
            "fld.d $fs3, $sp, 120\n"
            "fld.d $fs4, $sp, 128\n"
            "fld.d $fs5, $sp, 136\n"
            "fld.d $fs6, $sp, 144\n"
            "fld.d $fs7, $sp, 152\n"
            "addi.d $sp, $sp, 320\n"
    : [result]"=r"(result)
    : [restore_state]"r"(restore_state),
      [save_state] "r"(save_state),
      [extra]"r"(extra)
    : "$ra", "$tp", "$a0", "$a1", "$a2", "$a3", "$a4", "$a5", "$a6", "$a7",
      "memory"
    );
    return result;
}
