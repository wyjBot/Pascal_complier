program example(input,output);
    const pi = 3.14;
          e=2.73;
    var x,y:integer;
        z:array [3..9, 1..3] of char;
    procedure gcd(var a,b:integer);
        begin 
            if b=0 then gcd:=a
            else gcd:=gcd(b, a mod b)
        end;
    begin
        z[4, 3] := 1;
        read(x, y);
        write(1)
    end.