#ifndef _FILESYSTEM_H_
#define _FILESYSTEM_H_

#include "global.h"
#include "response.h"
#include "request.h"
#include "mytcp.h"

int createfile(char *name, struct Request *req);

struct FileInfo *file2body(char *path);

int GetFileLength(char *path);

int EndWithString(char *str1, char *str2);

void GetFileName(char *path, char *result);

void getType(char *file_name, char *extension);

#endif