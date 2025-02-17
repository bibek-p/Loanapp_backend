import React, { useEffect, useState } from 'react';
import { CreditCard } from '../../types/creditCard';
import { Box, Button, Table, TableBody, TableCell, TableHead, TableRow, Typography } from '@mui/material';
import { Add as AddIcon } from '@mui/icons-material';

interface Props {
  onEdit: (card: CreditCard) => void;
  onAdd: () => void;
  onDelete: (id: string) => void;
}

export const CreditCardList: React.FC<Props> = ({ onEdit, onAdd, onDelete }) => {
  const [cards, setCards] = useState<CreditCard[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCreditCards();
  }, []);

  const fetchCreditCards = async () => {
    try {
      const response = await fetch('/api/v1/loanapp/credit-cards/');
      const data = await response.json();
      setCards(data);
    } catch (error) {
      console.error('Error fetching credit cards:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <Typography>Loading...</Typography>;
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h5">Credit Cards</Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={onAdd}
        >
          Add New Card
        </Button>
      </Box>

      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Card Name</TableCell>
            <TableCell>Issuer</TableCell>
            <TableCell>Network</TableCell>
            <TableCell>Annual Fees</TableCell>
            <TableCell>Status</TableCell>
            <TableCell>Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {cards.map((card) => (
            <TableRow key={card.id}>
              <TableCell>{card.card_name}</TableCell>
              <TableCell>{card.issuer}</TableCell>
              <TableCell>{card.network}</TableCell>
              <TableCell>${card.annual_fees}</TableCell>
              <TableCell>{card.active_status ? 'Active' : 'Inactive'}</TableCell>
              <TableCell>
                <Button
                  variant="outlined"
                  color="primary"
                  size="small"
                  onClick={() => onEdit(card)}
                  sx={{ mr: 1 }}
                >
                  Edit
                </Button>
                <Button
                  variant="outlined"
                  color="error"
                  size="small"
                  onClick={() => onDelete(card.id)}
                >
                  Delete
                </Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </Box>
  );
}; 