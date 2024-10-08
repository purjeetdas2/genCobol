IDENTIFICATION DIVISION.
       PROGRAM-ID. EDI850Processor.
       AUTHOR. YourName.

       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT InputFile ASSIGN TO 'edi850.csv'
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT OutputFile ASSIGN TO 'output.csv'
               ORGANIZATION IS LINE SEQUENTIAL.

       DATA DIVISION.
       FILE SECTION.
       FD InputFile.
       01 InputRecord.
           05 PO-OrderID           PIC X(15).
           05 Filler1              PIC X.
           05 PO-BuyerID           PIC X(15).
           05 Filler2              PIC X.
           05 PO-Date              PIC X(08).
           05 Filler3              PIC X.
           05 PO-ItemID            PIC X(10).
           05 Filler4              PIC X.
           05 PO-ItemQuantity      PIC 9(05).
           05 Filler5              PIC X.
           05 PO-ItemUnitPrice     PIC 9(07)V99.

       FD OutputFile.
       01 OutputRecord.
           05 OutOrderID           PIC X(15).
           05 OutBuyerID           PIC X(15).
           05 OutDate              PIC X(08).
           05 OutItemID            PIC X(10).
           05 OutItemQuantity      PIC 9(05).
           05 OutItemTotalPrice    PIC 9(10)V99.

       WORKING-STORAGE SECTION.
       01 WS-InputData.
           05 WS-POOrderID         PIC X(15).
           05 WS-POBuyerID         PIC X(15).
           05 WS-PODate            PIC X(08).
           05 WS-POItemID          PIC X(10).
           05 WS-POItemQuantity    PIC 9(05).
           05 WS-POItemUnitPrice   PIC 9(07)V99.

       01 WS-OutputData.
           05 WS-OutOrderID        PIC X(15).
           05 WS-OutBuyerID        PIC X(15).
           05 WS-OutDate           PIC X(08).
           05 WS-OutItemID         PIC X(10).
           05 WS-OutItemQuantity   PIC 9(05).
           05 WS-OutItemTotalPrice PIC 9(10)V99.

       01 WS-EOF-FLAG              PIC X VALUE "N".
       01 WS-VALID-RECORD          PIC X VALUE "Y".

       PROCEDURE DIVISION.
       MAIN-PROCEDURE.
           OPEN INPUT InputFile.
           OPEN OUTPUT OutputFile.

           PERFORM UNTIL WS-EOF-FLAG = "Y"
               READ InputFile INTO InputRecord
               AT END
                   MOVE "Y" TO WS-EOF-FLAG
               NOT AT END
                   MOVE PO-OrderID TO WS-POOrderID
                   MOVE PO-BuyerID TO WS-POBuyerID
                   MOVE PO-Date TO WS-PODate
                   MOVE PO-ItemID TO WS-POItemID
                   MOVE PO-ItemQuantity TO WS-POItemQuantity
                   MOVE PO-ItemUnitPrice TO WS-POItemUnitPrice

                   PERFORM Validate-Record
                   IF WS-VALID-RECORD = "Y"
                       PERFORM Transform-Record
                       WRITE OutputRecord FROM WS-OutputData
                   ELSE
                       DISPLAY "Invalid record: " PO-OrderID
                   END-IF
               END-READ
           END-PERFORM.

           CLOSE InputFile.
           CLOSE OutputFile.

           STOP RUN.

       Validate-Record.
           IF WS-POItemQuantity < 0 OR WS-POItemUnitPrice < 0
               MOVE "N" TO WS-VALID-RECORD
           ELSE
               MOVE "Y" TO WS-VALID-RECORD
           END-IF.

       Transform-Record.
           MOVE WS-POOrderID TO WS-OutOrderID
           MOVE WS-POBuyerID TO WS-OutBuyerID
           MOVE WS-PODate TO WS-OutDate
           MOVE WS-POItemID TO WS-OutItemID
           MOVE WS-POItemQuantity TO WS-OutItemQuantity
           COMPUTE WS-OutItemTotalPrice = WS-POItemQuantity * WS-POItemUnitPrice.
           MOVE WS-OutOrderID TO OutOrderID
           MOVE WS-OutBuyerID TO OutBuyerID
           MOVE WS-OutDate TO OutDate
           MOVE WS-OutItemID TO OutItemID
           MOVE WS-OutItemQuantity TO OutItemQuantity
           MOVE WS-OutItemTotalPrice TO OutItemTotalPrice.
