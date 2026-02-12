# UI State Analysis - Aligned with 1.puml Flow

> **สร้างเมื่อ:** 2026-02-11
> **จุดประสงค์:** แนะนำแก้ UI State ให้ตรงกับ Activity Diagram (1.puml)

---

## 📊 สรุปความสอดคล้อง: **~45%**

ระบบปัจจุบันมี UI ครบฝั่ง User แต่ขาด **Staff/Officer** workflow pages

---

## 🎯 Flow ใน 1.puml vs UI ปัจจุบัน

### **Stage 1: Officer นำเข้า & ตรวจสอบโครงการ**

```
1.puml:
  |Officer| → Import Project
          → Check & Edit Project (PRJ Checking)
          → Assign Participants
          → Start PRJ

Current UI: ❌ NO STAFF PAGE
Recommend: ✅ Create staff_project_setup.html
```

**ต้องมี UI:**
- [ ] Import projects page (upload Excel/CSV)
- [ ] Project verification form (edit project details)
- [ ] Assign participants form (add users to project)
- [ ] Start project button

---

### **Stage 2: User สร้างใบสั่งซื้อ & Check Budget**

```
1.puml:
  |User|   → Create Order
          → Check Items & Budget
          
Status:    Draft → (check budget) → Order

Current UI: ✅ YES - create_order.html
            ✅ Budget check in API
Recommend: ✅ COMPLETE (no changes needed)
```

---

### **Stage 3: Officer Export & ระบุ Inspection Committee**

```
1.puml:
  |Officer| → Export file .xlsx
            → Specify Inspection Committee
            
Status: Ordering for Approval Loop

Current UI: ⚠️ PARTIAL - export buttons exist but unclear
Recommend: ✅ Enhance in staff approval page
```

**ต้องมี UI:**
- [ ] Staff approval page (view pending orders)
- [ ] Export to .xlsx button (for printing)
- [ ] Inspection committee selection form

---

### **Stage 4: Boss/Head Approval Loop**

```
1.puml:
  Decision: "การพิจารณาของหัวหน้า"
  
  Loop: Request → Head Review → 
        [แก้ไข] OR [อนุมัติ]

Current UI: ❌ NO BOSS PAGE
Recommend: ✅ Create boss_order_review.html
```

**ต้องมี UI:**
- [ ] Boss approval page (list unapproved orders)
- [ ] Order detail with approval form
- [ ] Approve/Reject/Request Correction buttons

---

### **Stage 5: Officer ส่งให้พัสดุ & Create Sub-order**

```
1.puml:
  |Officer| → Send to Procurement
           → Create Sub-order
           → Attach receipt/receipt images

Current UI: ⚠️ PARTIAL - API exists but no staff page
Recommend: ✅ Create staff_procurement.html
```

**ต้องมี UI:**
- [ ] Procurement management page (approved orders)
- [ ] Send to procurement button
- [ ] Sub-order creation form
- [ ] Receipt/invoice upload interface

---

### **Stage 6: Inspection Committee ตรวจรับ**

```
1.puml:
  Decision: "ถูกต้องครบถ้วน?"
  
  Path 1: ไม่ถูก → Reject Goods → End
  Path 2: ถูก   → Confirm Inspection → Continue

Current UI: ✅ PARTIAL - scan_order.html exists
Recommend: ✅ Add Confirm/Reject buttons
```

**ต้องมี UI:**
- [x] QR code scanning page (scan_order.html)
- [x] Item listing page
- [ ] **✅ ADD:** Confirm Inspection button
- [ ] **✅ ADD:** Reject Goods button + rejection reason form

---

### **Stage 7: System คำนวณ Budget**

```
1.puml:
  |System| → Calculate budget_spent
           → Update budget tracking

Current: ✅ API Level (OrderReceiveFromProcurementAPIView)
Recommend: ✅ NO UI CHANGE NEEDED
```

---

### **Stage 8: Officer ตั้งเบิกจ่ายเงิน (Ready for Payment)**

```
1.puml:
  |Officer| → "Ready for Payment" status
           → Payment Approval

Current UI: ❌ NO PAGE
Recommend: ✅ Create staff_payment_ready.html
```

**ต้องมี UI:**
- [ ] Payment ready page (completed orders)
- [ ] Mark as "Ready for Payment" button
- [ ] Payment tracking/summary

---

### **Stage 9: Close Project**

```
1.puml:
  Decision: "โครงการสำเร็จ?"
  
  If NO:  → Loop back to create order
  If YES: → Close Project formally

Current UI: ❌ NO PAGE
Recommend: ✅ Create project_closing.html
```

**ต้องมี UI:**
- [ ] Project summary page
- [ ] Final budget report
- [ ] Close project button
- [ ] Project closure confirmation

---

## 📋 UI Pages Checklist

### **Existing Pages (ที่มี):**
- ✅ `create_order.html` - User creates order
- ✅ `edit_order.html` - User edits draft
- ✅ `my_orders.html` - User views orders
- ✅ `order_detail.html` - View order details
- ✅ `receive_items.html` - Record delivery
- ✅ `scan_order.html` - Scan QR for inspection
- ✅ `order_qr.html` - Generate QR code
- ✅ `project_list.html` - List projects

### **Missing Staff Pages (ต้องเพิ่ม):**
- ❌ `staff_project_setup.html` - Import/verify/assign projects
- ❌ `staff_order_approval.html` - Review & approve orders
- ❌ `staff_inspection_committee.html` - Assign inspection committee
- ❌ `staff_send_procurement.html` - Send to procurement & create sub-orders
- ❌ `staff_payment_ready.html` - Mark ready for payment
- ❌ `staff_project_closing.html` - Close project

### **Missing Boss Pages (ต้องเพิ่ม):**
- ❌ `boss_order_review.html` - Review & approve/reject orders
- ❌ `boss_correction_request.html` - Request corrections

### **Enhancement Needed (ปรับปรุง):**
- ⚠️ `scan_order.html` - Add Confirm/Reject buttons
- ⚠️ Status badges - Add all 12 statuses in UI

---

## 🎨 UI State Status Mapping

### **Order Status Display Colors:**

```
Draft              🔵 Blue     - Not submitted
Pending            🟡 Yellow   - Waiting boss approval
WaitingBossApproval 🟡 Yellow  - Waiting boss
BossRejected       🔴 Red      - Rejected by boss
Approved           🟢 Green    - Approved by staff
SentToProcurement  🔵 Blue     - In procurement
WaitingInspection  🟠 Orange   - Waiting inspection
Inspected          🟢 Green    - Inspection done
RejectedGoods      🔴 Red      - Goods rejected
Received           🟢 Green    - Goods received
ReadyForPayment    🟢 Green    - Ready for payment
Closed             ⚫ Gray     - Order closed
Cancelled          ⚫ Gray     - Cancelled
CorrectionNeeded   🟠 Orange   - Need correction
```

---

## 🔧 Implementation Phases

### **Phase 1: Staff Core Pages (Week 1)**
```
✓ staff_project_setup.html
  - Import Excel
  - Verify project
  - Assign participants
  - Start project

✓ staff_order_approval.html
  - List pending orders
  - Review details
  - Approve/Reject/Request Correction
```

### **Phase 2: Procurement & Inspection (Week 2)**
```
✓ staff_send_procurement.html
  - View approved orders
  - Specify inspection committee
  - Send to procurement
  - Create sub-orders

✓ Enhanced scan_order.html
  - Add Confirm Inspection button
  - Add Reject Goods button
```

### **Phase 3: Boss & Payment (Week 3)**
```
✓ boss_order_review.html
  - List orders awaiting boss approval
  - Review & approve/reject

✓ staff_payment_ready.html
  - View completed orders
  - Mark as ready for payment
```

### **Phase 4: Project Lifecycle (Week 4)**
```
✓ staff_project_closing.html
  - Project summary
  - Final budget report
  - Close project
```

---

## 📝 Recommendations by Priority

### **🔴 CRITICAL (ต้องทำแล้ว):**
1. Add staff approval page (order review)
2. Add boss approval page
3. Add inspection confirm/reject buttons
4. Status badge colors for all 12 statuses

### **🟠 HIGH (สัปดาห์หน้า):**
5. Staff project setup page
6. Staff procurement page
7. Payment ready page

### **🟡 MEDIUM (เดือนหน้า):**
8. Project closing page
9. Enhanced reporting
10. Audit trail UI

---

## 💡 Quick Summary

**What to do:**
1. ✅ Update status badges with all 12 statuses
2. ✅ Create 6 missing staff/boss pages
3. ✅ Add Confirm/Reject buttons in inspection page
4. ✅ Link all pages in navigation

**What NOT to change:**
- ✅ Keep existing user pages as-is
- ✅ API layer is mostly complete
- ✅ Database schema is good

**Result:** UI will match 1.puml 100%

---

**Next Step:** Start Phase 1 - Create staff_project_setup.html & staff_order_approval.html

