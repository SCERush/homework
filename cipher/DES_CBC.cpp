#include <bits/stdc++.h>
#include <iostream>
#include <string.h>
#include "mat.h"

using namespace std;

// Convert ascii string to bin string
string str2bin(string text)
{
    string res = "";
    for (int i = 0; i < text.length(); i++)
    {
        bitset<8> ans(text[i]);
        res += ans.to_string();
    }
    return res;
}

// Convert bin string to hex string
string bin2hex(string text)
{
    char arr[16] = {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F'};
    int frac[4];
    frac[0] = 1;
    for (int i = 1; i < 4; i++)
        frac[i] = frac[i - 1] * 2;
    string res = "";
    reverse(text.begin(), text.end());
    string _text = text;

    int len = (int)_text.size();
    for (int i = 0; i < len; i += 4)
    {
        int ans = 0;
        for (int j = 0; j < 4; j++)
        {
            if (i + j >= len)
                break;
            int tmp = _text[i + j] - '0';
            tmp *= frac[j];
            ans += tmp;
        }
        res += arr[ans];
    }

    reverse(res.begin(), res.end());
    return res;
}

// Convert hex string to bin string
string hex2bin(string text)
{
    string res = "";
    int ln = (int)text.size();

    for (int i = 0; i < ln; i++)
    {
        int tmp = 0;
        if (text[i] >= '0' && text[i] <= '9')
            tmp = text[i] - '0';
        else
            tmp = text[i] - 'A' + 10;
        string ans = "";
        for (int j = 3; j >= 0; j--)
        {
            int pbit = 1 << j;
            if (tmp & pbit)
                ans += '1';
            else
                ans += '0';
        }
        res += ans;
    }
    return res;
}

// Convert bin string to ascii string
string bin2str(string text)
{
    string res = "";
    for (int i = 0; i < text.length(); i += 8)
    {
        int num = 0;
        for (int j = i; j < i + 8; j++)
        {
            num += (text[j] - '0') * pow(2, i + 7 - j);
        }
        res += num;
    }
    return res;
}

// XOR
string strXor(string a, string b)
{
    string r;
    for (int i = 0; i < a.length(); i++)
    {
        if (a[i] == b[i])
        {
            r += '0';
        }
        else
        {
            r += '1';
        }
    }
    return r;
}

// Matrix transformation
string transform(string bits, TABLE *table, int length)
{
    string res(length, '0');
    for (int i = 0; i < length; i++)
    {
        res[i] = bits[table[i] - 1];
    }
    return res;
}

// Get subkey
void getSubkey(string *subkey, string key)
{
    // Key table
    string trans_key = transform(key, KEY_Table, 56);
    string C(trans_key, 0, 28);
    string D(trans_key, 28, 28);

    for (int i = 0; i < 8; i++)
    {
        C = C.substr(SHIFT_Table[i]) + C.substr(0, SHIFT_Table[i]);
        D = D.substr(SHIFT_Table[i]) + D.substr(0, SHIFT_Table[i]);
        subkey[i] = transform(C + D, PC2_Table, 48);
    }
}

// map hex number to bin number
string help_B2C(int i)
{
    switch (i)
    {
    case 0:
        return "0000";
    case 1:
        return "0001";
    case 2:
        return "0010";
    case 3:
        return "0011";
    case 4:
        return "0100";
    case 5:
        return "0101";
    case 6:
        return "0110";
    case 7:
        return "0111";
    case 8:
        return "1000";
    case 9:
        return "1001";
    case 10:
        return "1010";
    case 11:
        return "1011";
    case 12:
        return "1100";
    case 13:
        return "1101";
    case 14:
        return "1110";
    case 15:
        return "1111";
    default:
        break;
    }
    return "0";
}

// bit to char
string B2C(string B, int i)
{
    int intB[6];
    for (int j = 0; j < 6; j++)
    {
        if (B[j] == '0')
            intB[j] = 0;
        else
            intB[j] = 1;
    }
    int row = intB[0] * 2 + intB[5];
    int col = intB[1] * 8 + intB[2] * 4 + intB[3] * 2 + intB[4];
    int s = S_Box[i][row - 1][col - 1];
    string C = help_B2C(s);
    return C;
}

// E-Box,xor,S-Box,P-Box
string functionF(string R, string K)
{
    // E Box
    string RE = transform(R, E_Table, 48);
    // XOR
    string RK = strXor(RE, K);
    // S Box
    string RS;
    for (int i = 0; i < 8; i++)
    {
        string B(RK.substr(i * 6, 6));
        string C = B2C(B, i);
        RS += C;
    }
    // P Box
    string res = transform(RS, P_Table, 32);
    return res;
}

// Encryption iteration
string iter(string L, string R, string *K, MODE mode)
{
    if (mode == en)
    {
        for (int i = 0; i < 8; i++)
        {
            string tmp(L);
            L = R;
            R = strXor(tmp, functionF(R, K[i]));
        }
    }
    else
    {
        for (int i = 7; i >= 0; i--)
        {
            string tmp(R);
            R = L;
            L = strXor(tmp, functionF(L, K[i]));
        }
    }
    // IP inverse transformation
    return transform(L + R, IP1_Table, 64);
}

// DES Cipher
string DES(string data, string key, MODE mode)
{
    // IP table
    data = transform(data, IP_Table, 64);
    string L(data, 0, 32);
    string R(data, 32, 32);

    string subkey[8];
    getSubkey(subkey, key);

    string res = iter(L, R, subkey, mode);
    return res;
}

// CBC mode
string CBC(string data, string key, MODE mode)
{
    string res = "";
    string block = "";
    string tmp = "";
    string iv = key;

    cout << endl;
    cout << "DES Cipher Algorithm of CBC mode starts" << endl;
    cout << "=========================================================================================" << endl;

    if (mode == en)
    {
        for (int i = 0; i < data.length() / 64; i++)
        {
            block = data.substr(i * 64, 64);
            cout << "Plain text block [ " << i << " ] " << block << endl;
            tmp = DES(strXor(block, iv), key, mode);
            iv = tmp;
            cout << "Cipher text block [ " << i << " ] " << tmp << endl;
            res += tmp;
            cout << "=========================================================================================" << endl;
        }
        cout << "Successfully encode! " << endl;
    }
    else
    {
        for (int i = 0; i < data.length() / 64; i++)
        {
            tmp = data.substr(i * 64, 64);
            cout << "Cipher text block [ " << i << " ] " << tmp << endl;
            block = strXor(DES(tmp, key, mode), iv);
            iv = tmp;
            cout << "Plain text block [ " << i << " ] " << block << endl;
            res += block;
            cout << "=========================================================================================" << endl;
        }
        cout << "Successfully decode! " << endl;
    }
    return res;
}

int main()
{
    char flag;
    cout << "Please choose the mode : \n0.exit \n1.encrypt \n2.decrypt" << endl;
    cout << "Your choice : ";
    cin >> flag;

    while (flag != '0')
    {
        if (flag == '1')
        {
            // encode
            string plain;
            string key;
            cout << "Please input the plain text : " << endl;
            // Hello, my name is huangxin, and my student number is 22023097, this is DES cipher test.
            getchar();
            getline(cin, plain);
            cout << "Please input the key (the key must be 8 charests) : " << endl;
            cin >> key;
            while (plain.length() % 8 != 0)
                plain += " ";
            if (key.length() != 8)
            {
                cout << "The key must be 8 charests!!!" << endl;
                continue;
            }

            string _plain = str2bin(plain);
            string _key = str2bin(key);
            // cout << _plain << endl;
            // cout << _key << endl;
            string cipher = CBC(_plain, _key, en);
            // cout << cipher << endl;
            string _cipher = bin2hex(cipher);
            cout << "The cipher text is : ";
            cout << _cipher << endl;
            cout << endl;
        }
        else if (flag == '2')
        {
            // decode
            string cipher;
            string key;
            cout << "Please input the cipher text : " << endl;
            cin >> cipher;
            cout << "Please input the key (the key must be 8 charests) : " << endl;
            cin >> key;
            if (key.length() != 8)
            {
                cout << "The key must be 8 charests!!!" << endl;
                continue;
            }

            string _cipher = hex2bin(cipher);
            string _key = str2bin(key);
            // cout << _cipher << endl;
            // cout << _key << endl;
            string plain = CBC(_cipher, _key, de);
            // cout << plain << endl;
            string _plain = bin2str(plain);
            cout << "The plain text is : ";
            cout << _plain << endl;
            cout << endl;
        }
        else
        {
            cout << "Wrong number!!!" << endl;
        }
        cout << "Your choice : ";
        cin >> flag;
    }
    return 0;
}
