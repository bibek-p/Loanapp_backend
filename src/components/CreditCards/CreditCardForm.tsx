import React from 'react';
import { useForm } from 'react-hook-form';
import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  TextField,
  Switch,
  FormControlLabel,
  Grid,
} from '@mui/material';
import { CreditCard, CreditCardFormData } from '../../types/creditCard';

interface Props {
  open: boolean;
  onClose: () => void;
  onSubmit: (data: CreditCardFormData) => void;
  initialData?: CreditCard;
}

export const CreditCardForm: React.FC<Props> = ({
  open,
  onClose,
  onSubmit,
  initialData,
}) => {
  const { register, handleSubmit, formState: { errors } } = useForm<CreditCardFormData>({
    defaultValues: initialData || {
      active_status: true,
      category_specific_reward_rates: {},
      meta_information: {},
    },
  });

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        {initialData ? 'Edit Credit Card' : 'Add New Credit Card'}
      </DialogTitle>
      <form onSubmit={handleSubmit(onSubmit)}>
        <DialogContent>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <TextField
                {...register('card_name', { required: 'Card name is required' })}
                label="Card Name"
                fullWidth
                error={!!errors.card_name}
                helperText={errors.card_name?.message}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                {...register('issuer', { required: 'Issuer is required' })}
                label="Issuer"
                fullWidth
                error={!!errors.issuer}
                helperText={errors.issuer?.message}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                {...register('network', { required: 'Network is required' })}
                label="Network"
                fullWidth
                error={!!errors.network}
                helperText={errors.network?.message}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                {...register('card_type', { required: 'Card type is required' })}
                label="Card Type"
                fullWidth
                error={!!errors.card_type}
                helperText={errors.card_type?.message}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                {...register('annual_fees', { 
                  required: 'Annual fees is required',
                  valueAsNumber: true 
                })}
                label="Annual Fees"
                type="number"
                fullWidth
                error={!!errors.annual_fees}
                helperText={errors.annual_fees?.message}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                {...register('apr_information')}
                label="APR Information"
                fullWidth
                multiline
                rows={2}
              />
            </Grid>
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    {...register('active_status')}
                    defaultChecked={initialData?.active_status ?? true}
                  />
                }
                label="Active Status"
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose}>Cancel</Button>
          <Button type="submit" variant="contained" color="primary">
            {initialData ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
}; 