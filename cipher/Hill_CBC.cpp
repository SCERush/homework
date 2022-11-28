#include <bits/stdc++.h>
#include <iostream>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sstream>
#include <unistd.h>
#include <gmp.h>
#define mod 256

using namespace std;

// Find modulo inverse of a with respect to m
int modInverse(int a, int m)
{
    a = a % m;
    for (int x = 1; x < m; x++)
        if ((a * x) % m == 1)
            return x;
    return 0;
}

// Allocate space to store matrix
mpz_t **allocateMatSpace(mpz_t **mat, int rows, int columns)
{
    mat = new mpz_t *[rows];
    for (int i = 0; i < rows; i++)
        mat[i] = new mpz_t[columns];
    return mat;
}

// Free the space used to store matrix
void deallocateMatSpace(mpz_t **mat, int rows, int columns)
{
    for (int i = 0; i < rows; i++)
        delete[] mat[i];
    delete[] mat;
}

// Print the matrix
void displayMatrix(mpz_t **mat, int rows, int cols)
{
    for (int i = 0; i < rows; i++)
    {
        for (int j = 0; j < cols; j++)
            cout << "|" << mat[i][j] << " ";
        cout << "|" << endl;
    }
}

// Find the cofactor of given matrix
void getCofactor(mpz_t **mat, mpz_t **cofac, int p, int q, int n)
{
    int i = 0, j = 0;
    for (int row = 0; row < n; row++)
    {
        for (int col = 0; col < n; col++)
        {
            if (row != p && col != q)
            {
                // cofac[i][j++] = mat[row][col];
                mpz_init_set(cofac[i][j++], mat[row][col]);
                if (j == n - 1)
                {
                    j = 0;
                    i++;
                }
            }
        }
    }
}

// Find the determinant of given matrix
void determinant(mpz_t ret, mpz_t **mat, int n)
{

    mpz_t det;
    mpz_init_set_str(det, "0", 10);
    if (n == 1)
    {
        mpz_init_set(ret, mat[0][0]);
        // return  mat[0][0];
        return;
    }

    mpz_t **temp;
    temp = allocateMatSpace(temp, n - 1, n - 1);
    int sign = 1;
    for (int i = 0; i < n; i++)
    {
        getCofactor(mat, temp, 0, i, n);

        mpz_t mul, detlocal;
        mpz_init_set_str(mul, "1", 10);
        mpz_init(detlocal);
        mpz_mul_si(mul, mul, sign);
        mpz_mul(mul, mul, mat[0][i]);

        determinant(detlocal, temp, n - 1);

        mpz_mul(mul, mul, detlocal);
        mpz_add(det, det, mul);
        sign = -sign;
    }
    deallocateMatSpace(temp, n - 1, n - 1);
    mpz_init_set(ret, det);
}

// Find adjoint of the matrix
void adjoint(mpz_t **mat, mpz_t **adj, int n)
{
    if (n == 1)
    {
        mpz_init_set_str(adj[0][0], "1", 10);
        return;
    }

    int sign = 1;

    mpz_t **temp;

    temp = allocateMatSpace(temp, n - 1, n - 1);
    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++)
        {
            getCofactor(mat, temp, i, j, n);
            sign = (i + j) % 2 == 0 ? 1 : -1;

            mpz_t det;
            mpz_init_set_str(det, "1", 10);
            determinant(det, temp, n - 1);
            mpz_mul_si(det, det, sign);
            mpz_init_set(adj[j][i], det);
        }
    deallocateMatSpace(temp, n - 1, n - 1);
}

// Find the inverse of matrix
void inverseMat(mpz_t **adj, int det, int n)
{
    int idet = modInverse(det, mod);
    cout << "Determinant: inverse " << idet << endl;
    if (idet == 0)
    {
        cout << "Inverse Modulo doesn't exist!!!\n";
    }
    cout << "Inverse modulo of " << det << " is " << idet << endl;
    for (int i = 0; i < n; i++)
    {
        for (int j = 0; j < n; j++)
        {
            mpz_t ad;
            mpz_init(ad);

            mpz_mul_ui(adj[i][j], adj[i][j], idet);
            mpz_t modulu;
            mpz_init_set_si(modulu, mod);
            mpz_mod(adj[i][j], adj[i][j], modulu);
        }
    }
}

// Print the 2-D vector
void display(vector<vector<int>> A)
{
    for (int i = 0; i < A.size(); i++)
    {
        for (int j = 0; j < A[i].size(); j++)
            cout << "|" << A[i][j] << " ";
        cout << "|" << endl;
    }
}

// Hill Cipher Encryption and Decryption
vector<vector<int>> hill(vector<vector<int>> text, vector<vector<int>> key)
{
    int i, j, k;
    vector<vector<int>> res;
    for (i = 0; i < text.size(); i++)
    {
        vector<int> temp;
        for (j = 0; j < key.size(); j++)
        {
            temp.push_back(0);
        }
        res.push_back(temp);
    }
    for (i = 0; i < text.size(); i++)
    {
        for (j = 0; j < key.size(); j++)
        {
            for (k = 0; k < key[j].size(); k++)
            {
                res[i][j] += text[i][k] * key[k][j];
            }
            res[i][j] = res[i][j] % mod;
        }
    }
    return res;
}

// Convert string into matrix
vector<vector<int>> toMatrix(string ptblock, int row, int col)
{
    int i, j, k = 0;
    vector<vector<int>> val;

    for (i = 0; i < row; i++)
    {
        vector<int> temp;
        for (j = 0; j < col; j++)
        {
            int x = (int)ptblock[k];
            temp.push_back(x);
            k++;
        }
        val.push_back(temp);
    }
    return val;
}

// Perform XOR operation
vector<vector<int>> xorop(vector<vector<int>> pt, vector<vector<int>> prevct)
{
    vector<vector<int>> ctop;

    int i, j;
    for (i = 0; i < pt.size(); i++)
    {
        vector<int> temp;
        for (j = 0; j < pt[i].size(); j++)
        {
            temp.push_back(pt[i][j] ^ prevct[i][j]);
        }
        ctop.push_back(temp);
    }
    return ctop;
}

// CBC Encryption
vector<vector<vector<int>>> cbcEncrypt(string pt, vector<vector<int>> key, int row, int col)
{
    vector<vector<int>> iv;
    vector<vector<int>> ct;
    for (int i = 0; i < row; i++)
    {
        vector<int> tm;
        for (int j = 0; j < col; j++)
        {
            tm.push_back(0);
        }
        iv.push_back(tm);
    }
    vector<vector<vector<int>>> chainct;
    chainct.push_back(iv);
    int pt_blksize = row * col;
    while (pt.size() % pt_blksize != 0)
    {
        pt += " ";
    }
    int i = 0;

    int iter = pt.size() / pt_blksize;
    cout << endl;
    cout << "Hill Cipher Algorithm of CBC mode starts" << endl;
    cout << "=====================================================" << endl;
    for (int l = 0; l < iter; l++)
    {
        vector<vector<int>> currpt;
        string substr = pt.substr(i, pt_blksize);

        currpt = toMatrix(substr, row, col);
        cout << "Plain text block[ " << l << " ]" << endl;
        display(currpt);

        ct = hill(xorop(currpt, iv), key);
        iv = ct;
        chainct.push_back(iv);
        cout << "\nCipher text block[ " << l << " ]" << endl;
        display(iv);
        cout << "=====================================================" << endl;
        i += pt_blksize;
    }

    return chainct;
}

// CBC Decryption
vector<vector<vector<int>>> cbcDecrypt(string str, vector<vector<int>> keyi, int row, int col)
{
    vector<vector<vector<int>>> ct;
    vector<int> st;
    vector<vector<int>> st2;
    int pt_blksize = row * col;
    int length = str.length() / 2;
    int rounds = length / pt_blksize;
    if (length % pt_blksize != 0)
        rounds += 1;
    int arr[length] = {0};
    int c = 0;
    for (int i = 0; i < length * 2; i += 2)
    {
        string a = str.substr(i, 2);
        unsigned int b;
        istringstream iss(a);
        iss >> hex >> b;
        arr[c] = b;
        c++;
    }
    c = 0;
    for (int i = 0; i < rounds; i++)
    {
        for (int j = 0; j < row; j++)
        {
            for (int k = 0; k < col; k++)
            {
                st.push_back(arr[c]);
                c++;
            }
            st2.push_back(st);
            st.clear();
        }
        ct.push_back(st2);
        st2.clear();
        st.clear();
    }
    vector<vector<vector<int>>> chainpt;
    vector<vector<int>> decry;
    vector<vector<int>> ivnew;
    for (int i = 0; i < row; i++)
    {
        vector<int> tm;
        for (int j = 0; j < col; j++)
        {
            tm.push_back(0);
        }
        ivnew.push_back(tm);
    }
    cout << endl;
    cout << "Decryption in CBC mode using Hill cipher" << endl;
    cout << "=====================================================" << endl;
    for (int i = 0; i < ct.size(); i++)
    {
        decry = hill(ct[i], keyi);
        cout << "Cipher text block[ " << i << " ]" << endl;
        display(ct[i]);
        cout << "\nPlain text block[ " << i << " ] is :" << endl;

        vector<vector<int>> exor = xorop(ivnew, decry);
        chainpt.push_back(exor);

        display(exor);
        cout << "=====================================================" << endl;
        ivnew = ct[i];
    }

    return chainpt;
}

// Get the key or key inverse
vector<vector<int>> getKeys(int num, char mode)
{
    mpz_t **key1;
    key1 = allocateMatSpace(key1, num, num);
    cout << "Enter the key matrix : \n";

    // [6 , 24, 1 ]
    // [13, 16, 10]
    // [20, 17, 15]
    for (int i = 0; i < num; i++)
        for (int j = 0; j < num; j++)
            cin >> key1[i][j];
    cout << "The key matrix is : " << endl;
    displayMatrix(key1, num, num);
    cout << "\n";

    mpz_t det;
    mpz_init_set_str(det, "1", 10);
    determinant(det, key1, num);
    cout << "The determinant of the matrix is : " << det << endl;

    mpz_t modulu;
    mpz_init_set_si(modulu, mod);

    if (mpz_cmp_si(det, 0) <= 0)
    {
        cout << "Inverse of " << det << " doesn't exist\n";
        exit(-1);
    }

    mpz_t **adj;

    adj = allocateMatSpace(adj, num, num);
    adjoint(key1, adj, num);
    int x = mpz_get_si(det);
    cout << x << "---";
    inverseMat(adj, x, num);

    vector<int> keystore;
    vector<vector<int>> key;
    vector<vector<int>> keyinv;

    for (int i = 0; i < num; i++)
    {
        for (int j = 0; j < num; j++)
        {
            int x = mpz_get_si(key1[i][j]);
            keystore.push_back(x);
        }
        key.push_back(keystore);
        keystore.clear();
    }
    deallocateMatSpace(key1, num, num);
    // inverse stored
    for (int i = 0; i < num; i++)
    {
        for (int j = 0; j < num; j++)
        {
            int x = mpz_get_si(adj[i][j]);
            keystore.push_back(x);
        }
        keyinv.push_back(keystore);
        keystore.clear();
    }
    if (mode == '1')
        return key;
    else
    {
        cout << "The inverse matrix of the key matrix is : " << endl;
        display(keyinv);
        return keyinv;
    }
}

// Convert cipher matrix to hex string
string to_hex(vector<vector<vector<int>>> ct)
{
    string res = "";
    for (int i = 1; i < ct.size(); i++)
    {
        for (int j = 0; j < ct[i].size(); j++)
        {
            for (int k = 0; k < ct[i][j].size(); k++)
            {
                int ans = ct[i][j][k];
                ostringstream ss;
                ss << setfill('0') << setw(2) << hex << ans;
                res += ss.str();
                // cout << "ans : " << ans << " hex : " << ss.str() << endl;
            }
        }
    }
    return res;
}

// Retrieving Original message from PT blocks obtained after Decryption
string to_char(vector<vector<vector<int>>> pt, int n)
{
    string res = "";
    int count = 0;

    count = 0;
    for (int i = 0; i < pt.size() /*&& count < n*/; i++)
    {
        for (int j = 0; j < pt[i].size() /*&& count < n*/; j++)
        {
            for (int k = 0; k < pt[i][j].size() /*&& count < n*/; k++)
            {
                int x = pt[i][j][k];
                res += char(x);
                count++;
            }
        }
    }
    return res;
}

int main()
{
    char flag;
    cout << "Please choose the mode : \n0.exit \n1.encrypt \n2.decrypt" << endl;
    cout << "Your choice : ";
    cin >> flag;
    
    if (flag != '1' && flag != '2')
    {
        cout << "Wrong number!!!" << endl;
    }

    string str;
    int num;

    cout << "\nEnter your string: ";
    // Hello, my name is huangxin, and my student number is 22023097, this is hill cipher test.
    getchar();
    getline(cin, str);
    int n = str.length();
    int row, col;
    int blksize;

    cout << "Enter the dimension of the key matrix : ";
    cin >> num;
    cout << "Enter the block size of the plain text,\nwhich should be multiple of dimension : ";
    cin >> blksize;
    cout << endl;

    row = blksize / num;
    col = num;

    if (flag == '1')
    {
        vector<vector<int>> key = getKeys(num, flag);
        // encrypt
        vector<vector<vector<int>>> CT = cbcEncrypt(str, key, row, col);
        string cipher = to_hex(CT);
        cout << "The cipher text is : " << cipher << endl;
        cout << endl
             << endl
             << endl;
    }
    else if (flag == '2')
    {
        vector<vector<int>> keyinv = getKeys(num, flag);
        // decrypt
        vector<vector<vector<int>>> PT = cbcDecrypt(str, keyinv, row, col);
        string plain = to_char(PT, n);
        cout << "\nThe plain text is : " << plain << endl;
        cout << endl
             << endl
             << endl;
    }

    return 0;
}
