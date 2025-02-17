import React, { useState } from 'react';
import { CreditCard, CreditCardFormData } from '../../types/creditCard';
import { CreditCardList } from './CreditCardList';
import { CreditCardForm } from './CreditCardForm';
import { useSnackbar } from 'notistack';

export const CreditCardManager: React.FC = () => {
  const [formOpen, setFormOpen] = useState(false);
  const [selectedCard, setSelectedCard] = useState<CreditCard | undefined>();
  const { enqueueSnackbar } = useSnackbar();

  const handleAdd = () => {
    setSelectedCard(undefined);
    setFormOpen(true);
  };

  const handleEdit = (card: CreditCard) => {
    setSelectedCard(card);
    setFormOpen(true);
  };

  const handleDelete = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this credit card?')) {
      try {
        const response = await fetch(`/api/v1/loanapp/credit-cards/delete/${id}/`, {
          method: 'DELETE',
        });

        if (response.ok) {
          enqueueSnackbar('Credit card deleted successfully', { variant: 'success' });
          // Refresh the list
          window.location.reload();
        } else {
          throw new Error('Failed to delete credit card');
        }
      } catch (error) {
        console.error('Error deleting credit card:', error);
        enqueueSnackbar('Failed to delete credit card', { variant: 'error' });
      }
    }
  };

  const handleSubmit = async (data: CreditCardFormData) => {
    try {
      const url = selectedCard
        ? `/api/v1/loanapp/credit-cards/update/${selectedCard.id}/`
        : '/api/v1/loanapp/credit-cards/add/';

      const response = await fetch(url, {
        method: selectedCard ? 'PUT' : 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      if (response.ok) {
        enqueueSnackbar(
          `Credit card ${selectedCard ? 'updated' : 'created'} successfully`,
          { variant: 'success' }
        );
        setFormOpen(false);
        // Refresh the list
        window.location.reload();
      } else {
        throw new Error(`Failed to ${selectedCard ? 'update' : 'create'} credit card`);
      }
    } catch (error) {
      console.error('Error submitting credit card:', error);
      enqueueSnackbar(
        `Failed to ${selectedCard ? 'update' : 'create'} credit card`,
        { variant: 'error' }
      );
    }
  };

  return (
    <>
      <CreditCardList
        onAdd={handleAdd}
        onEdit={handleEdit}
        onDelete={handleDelete}
      />
      <CreditCardForm
        open={formOpen}
        onClose={() => setFormOpen(false)}
        onSubmit={handleSubmit}
        initialData={selectedCard}
      />
    </>
  );
}; 