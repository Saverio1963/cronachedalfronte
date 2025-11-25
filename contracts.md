# API Contracts - Sito Libro "Cronache dal fronte invisibile"

## Overview
Questo documento definisce i contratti API tra frontend e backend per il sito web del libro.

## Mocked Data (Frontend Only)
- **File**: `/app/frontend/src/data/mock.js`
- **Contenuto**: Dati del libro (titolo, autore, sinossi, biografia, citazione, link acquisto)
- **Stato**: ✅ Implementato - nessun backend necessario

## Backend API Implementation

### 1. Contact Form API

**Endpoint**: `POST /api/contacts`

**Purpose**: Salvare messaggi di contatto dal form nel database

**Request Body**:
```json
{
  "name": "string",
  "email": "string",
  "message": "string"
}
```

**Validation**:
- `name`: required, min 2 chars, max 100 chars
- `email`: required, valid email format
- `message`: required, min 10 chars, max 2000 chars

**Response Success (200)**:
```json
{
  "success": true,
  "message": "Messaggio ricevuto con successo",
  "contact_id": "uuid"
}
```

**Response Error (400)**:
```json
{
  "success": false,
  "error": "Validation error message"
}
```

**Response Error (500)**:
```json
{
  "success": false,
  "error": "Server error message"
}
```

### 2. MongoDB Collection

**Collection Name**: `contacts`

**Schema**:
```json
{
  "_id": "ObjectId",
  "contact_id": "string (uuid)",
  "name": "string",
  "email": "string",
  "message": "string",
  "created_at": "datetime",
  "status": "string (new|read|replied)"
}
```

**Indexes**:
- `contact_id`: unique
- `created_at`: descending
- `email`: non-unique

## Frontend Integration

### File to Update: `/app/frontend/src/components/ContactForm.jsx`

**Changes Required**:
1. Remove mock setTimeout submission
2. Add axios call to `POST /api/contacts`
3. Handle success/error responses
4. Show appropriate toast messages

**Current Mock Code** (to replace):
```javascript
setTimeout(() => {
  toast({
    title: "Messaggio inviato!",
    description: "Ti risponderemo al più presto.",
  });
  setFormData({ name: '', email: '', message: '' });
  setIsSubmitting(false);
}, 1000);
```

**New Real Code**:
```javascript
try {
  const response = await axios.post(`${BACKEND_URL}/api/contacts`, formData);
  toast({
    title: "Messaggio inviato!",
    description: "Ti risponderemo al più presto.",
  });
  setFormData({ name: '', email: '', message: '' });
} catch (error) {
  toast({
    title: "Errore",
    description: error.response?.data?.error || "Impossibile inviare il messaggio",
    variant: "destructive"
  });
} finally {
  setIsSubmitting(false);
}
```

## Testing Checklist

### Backend Testing
- [ ] POST /api/contacts with valid data returns 200
- [ ] POST /api/contacts with invalid email returns 400
- [ ] POST /api/contacts with missing fields returns 400
- [ ] POST /api/contacts with empty message returns 400
- [ ] Verify data is saved in MongoDB `contacts` collection
- [ ] Verify unique contact_id is generated

### Frontend Testing
- [ ] Form validation works (required fields)
- [ ] Submit button disabled during submission
- [ ] Success toast appears after successful submission
- [ ] Error toast appears on failure
- [ ] Form resets after successful submission
- [ ] Loading state shows correctly

### Integration Testing
- [ ] Frontend successfully sends data to backend
- [ ] Backend saves data to database
- [ ] Frontend receives and displays success/error correctly
- [ ] Test with various message lengths
- [ ] Test with special characters in message
- [ ] Test with invalid email formats
