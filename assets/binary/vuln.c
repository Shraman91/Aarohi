#include <stdio.h>
#include <string.h>

// Forward declaration since gets() was removed from modern stdio.h (C11+)
char *gets(char *s);

// In the production environment, the flag is read from the secure vault upon hijack
void emit_flag() {
  FILE *f = fopen("flag.txt", "r");
  if (f) {
    char buf[64];
    if (fgets(buf, sizeof(buf), f)) {
      printf("%s", buf);
    }
    fclose(f);
  } else {
    printf("[VAULT LOCKED] Flag emitted from secure vault upon hijack.\n");
  }
}

void win() {
  emit_flag();
}

void login() {
  char password[32];
  printf("Enter password: ");
  gets(password);
  printf("Access denied.\n");
}

int main() {
  login();
  return 0;
}
